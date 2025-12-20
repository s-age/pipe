"""Service for Gemini API client operations."""

import base64
import json
import os
import zoneinfo
from collections.abc import Generator
from typing import TYPE_CHECKING, TypedDict

import google.genai as genai
from google.genai import types
from jinja2 import Environment, FileSystemLoader
from pipe.core.domains.gemini_cache import GeminiCache
from pipe.core.models.unified_chunk import (
    MetadataChunk,
    TextChunk,
    ToolCallChunk,
    UnifiedChunk,
    UsageMetadata,
)
from pipe.core.repositories.streaming_log_repository import StreamingLogRepository
from pipe.core.services.gemini_cache_service import GeminiCacheService
from pipe.core.services.gemini_tool_service import GeminiToolService
from pipe.core.services.token_service import TokenService
from pipe.core.utils.datetime import get_current_datetime

if TYPE_CHECKING:
    from pipe.core.services.prompt_service import PromptService
    from pipe.core.services.session_service import SessionService


class LogUsageInfo(TypedDict):
    prompt_tokens: int | None
    candidates_tokens: int | None
    total_tokens: int | None
    cached_content_tokens: int | None


class LogInfo(TypedDict):
    has_candidates: bool
    finish_reason: str | None
    text_content: str
    usage: LogUsageInfo | None


class GeminiClientService:
    """
    Manages Gemini API client operations and streaming.

    Responsibilities:
    - Build and render prompts (static/dynamic split for caching)
    - Load tools via ToolService
    - Manage cache via GeminiCacheService
    - Execute API streaming calls
    - Log streaming chunks using StreamingLogRepository

    Note:
        This service orchestrates the API call flow but delegates
        specific concerns to specialized services (Tool, Cache, Token).
    """

    def __init__(self, session_service: "SessionService"):
        """
        Initialize the Gemini client service.

        Args:
            session_service: Session service for accessing session data and settings
        """
        self.session_service = session_service
        self.settings = session_service.settings
        self.project_root = session_service.project_root

        # Initialize sub-services
        self.tool_service = GeminiToolService()
        self.cache_service = GeminiCacheService(self.project_root, self.settings)
        self.token_service = TokenService(settings=self.settings)
        self.last_raw_response: str | None = None

        # Convert timezone string to ZoneInfo object
        try:
            self.timezone = zoneinfo.ZoneInfo(self.settings.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            # Fallback to UTC if timezone not found
            self.timezone = zoneinfo.ZoneInfo("UTC")

    def stream_content(
        self, prompt_service: "PromptService"
    ) -> Generator[UnifiedChunk, None, None]:
        """
        Execute Gemini API call with streaming and return UNIFIED CHUNKS.

        Flow:
        1. Build prompt model (PromptService)
        2. Render static/dynamic templates with Jinja2
        3. Load tools (GeminiToolService)
        4. Check token limits (TokenService)
        5. Determine cache strategy (GeminiCache domain)
        6. Create/retrieve cache (GeminiCacheService)
        7. Execute streaming API call
        8. Log chunks (StreamingLogRepository with append mode)
        9. Yield standardized Pydantic chunks (model-agnostic format)

        Unified Chunk Types:
            - TextChunk: Text content from model
            - ToolCallChunk: Tool call request
            - MetadataChunk: Usage metadata

        Args:
            prompt_service: Service for building prompts

        Yields:
            Pydantic UnifiedChunk instances (TextChunk | ToolCallChunk | MetadataChunk)

        Raises:
            ValueError: If prompt exceeds token limit
            RuntimeError: If API call fails
        """
        session_data = self.session_service.current_session

        # Set session ID in environment for tools to access
        os.environ["PIPE_SESSION_ID"] = session_data.session_id

        # 1. Build prompt model
        prompt_model = prompt_service.build_prompt(self.session_service)
        context = prompt_model.model_dump()

        # 2. Render static and dynamic content
        static_content, dynamic_content = self._render_prompt_templates(
            prompt_service, context
        )

        # 3. Prepare Buffered History as Content objects
        buffered_contents: list[types.Content] = []
        if prompt_model.buffered_history and prompt_model.buffered_history.turns:
            turns = prompt_model.buffered_history.turns
            for i, turn in enumerate(turns):
                # Only pass raw_response to the LAST turn if it's a model response
                is_last = i == len(turns) - 1
                raw_resp = prompt_model.raw_response if is_last else None
                content_obj = self._convert_turn_to_content(turn, raw_resp)
                buffered_contents.append(content_obj)

        # 4. Prepare Current Task Content
        current_task_content = None
        if prompt_model.current_task and prompt_model.current_task.instruction.strip():
            current_task_content = types.Content(
                role="user",
                parts=[types.Part(text=prompt_model.current_task.instruction)],
            )

        # 5. Load tools
        loaded_tools_data = self.tool_service.load_tools(self.project_root)

        # 6. Check token limits
        full_text = (static_content or "") + dynamic_content
        token_count = self.token_service.count_tokens(
            full_text, tools=loaded_tools_data
        )

        is_within_limit, message = self.token_service.check_limit(token_count)
        if not is_within_limit:
            raise ValueError("Prompt exceeds context window limit. Aborting.")

        # 7. Convert tools to Gemini types
        converted_tools = self._convert_tools(loaded_tools_data)

        # 8. Initialize API client
        client = genai.Client()

        # 9. Determine cache strategy and prepare content
        gemini_cache = GeminiCache(
            tool_response_limit=self.settings.tool_response_expiration,
            cache_update_threshold=self.settings.model.cache_update_threshold,
        )
        cached_content_name, content_to_send = self._prepare_cache_and_content(
            client=client,
            gemini_cache=gemini_cache,
            session_data=session_data,
            static_content=static_content,
            dynamic_content=dynamic_content,
            converted_tools=converted_tools,
            buffered_history_contents=buffered_contents,
            current_task_content=current_task_content,
        )

        # 10. Build generation config
        config = self._build_generation_config(
            session_data=session_data,
            cached_content_name=cached_content_name,
            converted_tools=converted_tools,
        )

        # 11. Execute streaming call with logging
        yield from self._execute_streaming_call(
            client=client,
            content_to_send=content_to_send,
            config=config,
            session_data=session_data,
        )

    def _render_prompt_templates(
        self, prompt_service: "PromptService", context: dict
    ) -> tuple[str, str]:
        """
        Render static and dynamic prompt templates.

        Args:
            prompt_service: Prompt service instance
            context: Context dictionary for template rendering

        Returns:
            Tuple of (static_content, dynamic_content)
        """
        template_env = Environment(
            loader=FileSystemLoader(
                os.path.join(prompt_service.project_root, "templates", "prompt")
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        static_content = ""
        dynamic_content = ""

        try:
            # Render static template (cached)
            static_template = template_env.get_template("gemini_static_prompt.j2")
            static_content = static_template.render(session=context)

            # Render dynamic template (not cached)
            dynamic_template = template_env.get_template("gemini_dynamic_prompt.j2")
            dynamic_content = dynamic_template.render(session=context)

        except Exception:
            # Fallback: use monolithic template (no caching)
            template = template_env.get_template("gemini_api_prompt.j2")
            dynamic_content = template.render(session=context)
            static_content = ""

        return static_content, dynamic_content

    def _convert_tools(self, loaded_tools_data: list[dict]) -> list[types.Tool]:
        """
        Convert tool definitions to Gemini API types.

        Args:
            loaded_tools_data: List of tool definition dicts

        Returns:
            List of types.Tool objects
        """
        converted_tools = []
        for tool_data in loaded_tools_data:
            parameters_schema = types.Schema(**tool_data.get("parameters", {}))
            converted_tools.append(
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=tool_data["name"],
                            description=tool_data.get("description", ""),
                            parameters=parameters_schema,
                        )
                    ]
                )
            )
        return converted_tools

    def _prepare_cache_and_content(
        self,
        client: genai.Client,
        gemini_cache: GeminiCache,
        session_data,
        static_content: str,
        dynamic_content: str,
        converted_tools: list[types.Tool],
        buffered_history_contents: list[types.Content],
        current_task_content: types.Content | None,
    ) -> tuple[str | None, list[types.Content | str]]:
        """
        Determine cache strategy and prepare content to send.

        Args:
            client: Gemini API client
            gemini_cache: Cache domain logic
            session_data: Current session data
            static_content: Static prompt content
            dynamic_content: Dynamic prompt content
            converted_tools: Converted tool definitions
            buffered_history_contents: List of buffered turns as Content objects
            current_task_content: Content object for the current task (optional)

        Returns:
            Tuple of (cached_content_name, content_list_to_send)
        """
        # Calculate buffered tokens (not yet cached)
        buffered_tokens = (
            session_data.token_count - session_data.cached_content_token_count
            if session_data.cached_content_token_count > 0
            else session_data.token_count
        )

        should_cache = gemini_cache.should_update_cache(buffered_tokens)

        # Setup logging repository for cache decisions
        streaming_log_repo = StreamingLogRepository(
            self.project_root, session_data.session_id, self.settings
        )
        streaming_log_repo.open(mode="a")

        cached_content_name = None
        content_to_send: list[types.Content | str] = []

        try:
            if should_cache and static_content:
                # Create/update cache
                cache_msg = (
                    f"Cache decision: CREATING/UPDATING cache. "
                    f"Current cached_tokens={session_data.cached_content_token_count}, "
                    f"Current prompt_tokens={session_data.token_count}, "
                    f"Buffered tokens={buffered_tokens}"
                )
                streaming_log_repo.write_log_line(
                    "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
                )

                cached_content_name = self.cache_service.get_cached_content(
                    client,
                    static_content,
                    self.token_service.model_name,
                    converted_tools,
                )

            elif not session_data.cached_content_token_count:
                # No cache exists, below threshold: send all
                cache_msg = (
                    f"Cache decision: NO CACHE (below threshold). "
                    f"Current prompt_tokens={session_data.token_count}, "
                    f"Threshold={gemini_cache.cache_update_threshold}. "
                    f"Sending static + dynamic content"
                )
                streaming_log_repo.write_log_line(
                    "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
                )
                if static_content:
                    content_to_send.append(static_content)

            else:
                # Use existing cache
                cache_msg = (
                    f"Cache decision: USING EXISTING cache (buffered below threshold). "
                    f"Current cached_tokens={session_data.cached_content_token_count}, "
                    f"Current prompt_tokens={session_data.token_count}, "
                    f"Buffered tokens={buffered_tokens}, "
                    f"Threshold={gemini_cache.cache_update_threshold}"
                )
                streaming_log_repo.write_log_line(
                    "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
                )

                if static_content:
                    try:
                        cached_content_name = self.cache_service.get_cached_content(
                            client,
                            static_content,
                            self.token_service.model_name,
                            converted_tools,
                        )
                    except Exception:
                        # Fallback if cache retrieval fails
                        content_to_send.append(static_content)

        finally:
            streaming_log_repo.close()

        # Order: Dynamic (Context) -> Buffered History -> Current Task
        content_to_send.append(dynamic_content)
        content_to_send.extend(buffered_history_contents)
        if current_task_content:
            content_to_send.append(current_task_content)

        return cached_content_name, content_to_send

    def _build_generation_config(
        self,
        session_data,
        cached_content_name: str | None,
        converted_tools: list[types.Tool],
    ) -> types.GenerateContentConfig:
        """
        Build generation configuration for API call.

        Args:
            session_data: Current session data
            cached_content_name: Cache name if using cache
            converted_tools: Tool definitions

        Returns:
            Generation config object
        """
        # Base parameters from settings
        gen_config_params = {
            "temperature": self.settings.parameters.temperature.value,
            "top_p": self.settings.parameters.top_p.value,
            "top_k": self.settings.parameters.top_k.value,
        }

        # Override with session hyperparameters if present
        if session_params := session_data.hyperparameters:
            if temp_val := session_params.temperature:
                gen_config_params["temperature"] = temp_val
            if top_p_val := session_params.top_p:
                gen_config_params["top_p"] = top_p_val
            if top_k_val := session_params.top_k:
                gen_config_params["top_k"] = top_k_val

        # If using cache, don't pass tools again (they're in the cache)
        return types.GenerateContentConfig(
            tools=None if cached_content_name else converted_tools,  # type: ignore[arg-type]
            temperature=gen_config_params.get("temperature"),
            top_p=gen_config_params.get("top_p"),
            top_k=gen_config_params.get("top_k"),
            cached_content=cached_content_name,
        )

    def _execute_streaming_call(
        self,
        client: genai.Client,
        content_to_send: list[types.Content | str] | str,
        config: types.GenerateContentConfig,
        session_data,
    ) -> Generator[UnifiedChunk, None, None]:
        """
        Execute streaming API call with chunk logging and unified format conversion.

        Args:
            client: Gemini API client
            content_to_send: Prompt content to send
            config: Generation configuration
            session_data: Current session data

        Yields:
            Unified Pydantic chunk models (model-agnostic format)

        Raises:
            RuntimeError: If API call fails
        """
        raw_chunk_repo = StreamingLogRepository(
            self.project_root, session_data.session_id, self.settings
        )
        raw_chunk_repo.open(mode="a")

        collected_chunks = []

        try:
            stream = client.models.generate_content_stream(
                contents=content_to_send,
                config=config,
                model=self.token_service.model_name,
            )

            for chunk in stream:
                collected_chunks.append(chunk)

                # Log raw chunk (extract text and usage, skip binary fields)
                try:
                    log_info: LogInfo = {
                        "has_candidates": bool(chunk.candidates),
                        "finish_reason": None,
                        "text_content": "",
                        "usage": None,
                    }

                    if chunk.candidates:
                        candidate = chunk.candidates[0]
                        log_info["finish_reason"] = (
                            str(candidate.finish_reason)
                            if candidate.finish_reason
                            else None
                        )

                        if candidate.content and candidate.content.parts:
                            for part in candidate.content.parts:
                                if part.text is not None:
                                    log_info["text_content"] = part.text
                                    break

                    if chunk.usage_metadata:
                        log_usage: LogUsageInfo = {
                            "prompt_tokens": chunk.usage_metadata.prompt_token_count,
                            "candidates_tokens": (
                                chunk.usage_metadata.candidates_token_count
                            ),
                            "total_tokens": chunk.usage_metadata.total_token_count,
                            "cached_content_tokens": (
                                chunk.usage_metadata.cached_content_token_count
                            ),
                        }
                        log_info["usage"] = log_usage

                    raw_chunk_repo.write_log_line(
                        "RAW_CHUNK",
                        json.dumps(log_info, ensure_ascii=False),
                        get_current_datetime(self.timezone),
                    )
                except Exception:
                    pass

                # Convert Gemini chunk to unified format
                unified_chunks = self._convert_chunk_to_unified_format(chunk)
                yield from unified_chunks

            # After stream completes, try to extract thought signature and save
            # raw response
            target_chunk = None
            if collected_chunks:
                # Prioritize finding chunk with thought_signature
                for c in collected_chunks:
                    if (
                        c.candidates
                        and c.candidates[0].content
                        and c.candidates[0].content.parts
                    ):
                        for p in c.candidates[0].content.parts:
                            if p.thought_signature:
                                target_chunk = c
                                break
                    if target_chunk:
                        break

                # Fallback to last chunk if no signature found (to keep usage metadata)
                if not target_chunk:
                    target_chunk = collected_chunks[-1]

                if target_chunk:
                    # Persist serialized chunk to session object (in memory)
                    # The SessionService will persist this to disk when saving
                    # the session
                    try:
                        self.last_raw_response = target_chunk.model_dump_json()
                    except Exception:
                        pass

        except Exception as e:
            raise RuntimeError(f"Error during Gemini API execution: {e}")
        finally:
            raw_chunk_repo.close()

    def _convert_chunk_to_unified_format(
        self, chunk: types.GenerateContentResponse
    ) -> list[UnifiedChunk]:
        """
        Convert Gemini API chunk to unified Pydantic format.

        Args:
            chunk: Raw Gemini API response chunk

        Returns:
            List of unified Pydantic chunk models
        """
        unified_chunks: list[UnifiedChunk] = []

        # Extract candidates if present
        if chunk.candidates and len(chunk.candidates) > 0:
            candidate = chunk.candidates[0]
            if candidate.content and candidate.content.parts:
                # Extract text content and tool calls
                for part in candidate.content.parts:
                    if part.text is not None:
                        unified_chunks.append(TextChunk(content=part.text))
                    elif hasattr(part, "function_call") and part.function_call:
                        unified_chunks.append(
                            ToolCallChunk(
                                name=part.function_call.name,
                                args=dict(part.function_call.args or {}),
                            )
                        )

        # Extract usage metadata (typically on final chunk)
        if chunk.usage_metadata:
            unified_chunks.append(
                MetadataChunk(
                    usage=UsageMetadata(
                        prompt_token_count=chunk.usage_metadata.prompt_token_count,
                        candidates_token_count=chunk.usage_metadata.candidates_token_count,
                        total_token_count=chunk.usage_metadata.total_token_count,
                        cached_content_token_count=chunk.usage_metadata.cached_content_token_count,
                    )
                )
            )

        return unified_chunks

    def _restore_thought_signature(
        self, raw_response_json: str
    ) -> types.Content | None:
        """Restores content with thought signature from raw response JSON."""
        try:
            # Pydantic automatic validation
            response = types.GenerateContentResponse.model_validate_json(
                raw_response_json
            )
            if not response.candidates or not response.candidates[0].content:
                return None

            content = response.candidates[0].content

            # Manual base64 decode for thought_signature
            if content.parts:
                for part in content.parts:
                    if part.thought_signature:
                        if isinstance(part.thought_signature, str):
                            part.thought_signature = base64.b64decode(
                                part.thought_signature
                            )
            return content
        except Exception:
            return None

    def _convert_turn_to_content(
        self, turn, raw_response: str | None = None
    ) -> types.Content:
        """Converts a Turn model to a Gemini Content object."""
        role = "user"
        parts = []

        # Determine role and basic text content
        if hasattr(turn, "type"):
            if turn.type == "user_task":
                role = "user"
                parts.append(types.Part(text=turn.instruction))
            elif turn.type == "model_response":
                role = "model"
                # If this is the latest model turn and we have a raw response,
                # try to restore signature
                if raw_response:
                    restored = self._restore_thought_signature(raw_response)
                    if restored:
                        return restored

                parts.append(types.Part(text=turn.content))
            elif turn.type == "function_calling":
                role = "model"
                # Simplistic text representation for now
                parts.append(types.Part(text=f"Function Call: {turn.response}"))
            elif turn.type == "tool_response":
                role = "user"
                # Simplistic representation
                parts.append(
                    types.Part(text=f"Tool Response ({turn.name}): {turn.response}")
                )

        return types.Content(role=role, parts=parts)
