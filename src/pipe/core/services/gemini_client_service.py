"""Service for Gemini API client operations."""

import json
import os
from collections.abc import Generator
from datetime import datetime
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    from pipe.core.services.prompt_service import PromptService
    from pipe.core.services.session_service import SessionService


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
        self.cache_service = GeminiCacheService(self.project_root)
        self.token_service = TokenService(settings=self.settings)

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

        sessions_dir = os.path.join(self.project_root, "sessions")

        # 1. Build prompt model
        prompt_model = prompt_service.build_prompt(self.session_service)
        context = prompt_model.model_dump()

        # 2. Render static and dynamic content
        static_content, dynamic_content = self._render_prompt_templates(
            prompt_service, context
        )

        # 3. Load tools
        loaded_tools_data = self.tool_service.load_tools(self.project_root)

        # 4. Check token limits
        full_text = (static_content or "") + dynamic_content
        token_count = self.token_service.count_tokens(
            full_text, tools=loaded_tools_data
        )

        is_within_limit, message = self.token_service.check_limit(token_count)
        if not is_within_limit:
            raise ValueError("Prompt exceeds context window limit. Aborting.")

        # 5. Convert tools to Gemini types
        converted_tools = self._convert_tools(loaded_tools_data)

        # 6. Initialize API client
        client = genai.Client()

        # 7. Determine cache strategy and prepare content
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
            sessions_dir=sessions_dir,
        )

        # 8. Build generation config
        config = self._build_generation_config(
            session_data=session_data,
            cached_content_name=cached_content_name,
            converted_tools=converted_tools,
        )

        # 9. Execute streaming call with logging
        yield from self._execute_streaming_call(
            client=client,
            content_to_send=content_to_send,
            config=config,
            session_data=session_data,
            sessions_dir=sessions_dir,
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
        sessions_dir: str,
    ) -> tuple[str | None, str]:
        """
        Determine cache strategy and prepare content to send.

        Args:
            client: Gemini API client
            gemini_cache: Cache domain logic
            session_data: Current session data
            static_content: Static prompt content
            dynamic_content: Dynamic prompt content
            converted_tools: Converted tool definitions
            sessions_dir: Sessions directory path

        Returns:
            Tuple of (cached_content_name, content_to_send)
        """
        # Calculate buffered tokens (not yet cached)
        buffered_tokens = (
            session_data.token_count - session_data.cached_content_token_count
            if session_data.cached_content_token_count > 0
            else session_data.token_count
        )

        should_cache = gemini_cache.should_update_cache(buffered_tokens)

        # Setup logging repository for cache decisions
        log_file_path = os.path.join(
            sessions_dir, f"{session_data.session_id}.streaming.log"
        )
        streaming_log_repo = StreamingLogRepository(log_file_path)
        streaming_log_repo.open(mode="a")

        cached_content_name = None
        content_to_send = dynamic_content

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
                    "CACHE_DECISION", cache_msg, datetime.now()
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
                    "CACHE_DECISION", cache_msg, datetime.now()
                )
                content_to_send = static_content + "\n" + dynamic_content

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
                    "CACHE_DECISION", cache_msg, datetime.now()
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
                        content_to_send = static_content + "\n" + dynamic_content

        finally:
            streaming_log_repo.close()

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
        content_to_send: str,
        config: types.GenerateContentConfig,
        session_data,
        sessions_dir: str,
    ) -> Generator[UnifiedChunk, None, None]:
        """
        Execute streaming API call with chunk logging and unified format conversion.

        Args:
            client: Gemini API client
            content_to_send: Prompt content to send
            config: Generation configuration
            session_data: Current session data
            sessions_dir: Sessions directory path

        Yields:
            Unified Pydantic chunk models (model-agnostic format)

        Raises:
            RuntimeError: If API call fails
        """
        log_file_path = os.path.join(
            sessions_dir, f"{session_data.session_id}.streaming.log"
        )
        raw_chunk_repo = StreamingLogRepository(log_file_path)
        raw_chunk_repo.open(mode="a")

        try:
            stream = client.models.generate_content_stream(
                contents=content_to_send,
                config=config,
                model=self.token_service.model_name,
            )

            for chunk in stream:
                # Log raw chunk
                try:
                    if hasattr(chunk, "to_dict"):
                        chunk_dict = chunk.to_dict()  # type: ignore[attr-defined]
                    else:
                        chunk_dict = {"raw": str(chunk)}
                    raw_chunk_repo.write_log_line(
                        "RAW_CHUNK",
                        json.dumps(chunk_dict, ensure_ascii=False, default=str),
                        datetime.now(),
                    )
                except Exception:
                    try:
                        raw_chunk_repo.write_log_line(
                            "RAW_CHUNK",
                            json.dumps({"raw": str(chunk)}, ensure_ascii=False),
                            datetime.now(),
                        )
                    except Exception:
                        pass

                # Convert Gemini chunk to unified format
                unified_chunks = self._convert_chunk_to_unified_format(chunk)
                yield from unified_chunks

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

        # Safely extract candidates
        if not chunk.candidates or len(chunk.candidates) == 0:
            return unified_chunks

        candidate = chunk.candidates[0]
        if not candidate.content or not candidate.content.parts:
            return unified_chunks

        # Extract text content and tool calls
        for part in candidate.content.parts:
            if part.text:
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
