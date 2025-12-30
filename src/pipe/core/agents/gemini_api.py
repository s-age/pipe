# This script utilizes the 'google-genai' library to interact with the Gemini API.
# It is important to note that 'google-genai' is the newer, recommended library,
# and should be used in place of the older 'google-generativeai' library to ensure
# access to the latest features and improvements.
# For reference, see: https://pypi.org/project/google-genai/

import os
import zoneinfo
from collections.abc import Generator
from typing import TYPE_CHECKING

import google.genai as genai
from google.genai import types
from pipe.core.agents import register_agent
from pipe.core.agents.base import BaseAgent
from pipe.core.domains import gemini_token_count
from pipe.core.domains.gemini_api_payload import GeminiApiPayloadBuilder
from pipe.core.domains.gemini_api_stream_processor import GeminiApiStreamProcessor
from pipe.core.domains.gemini_payload_service import GeminiPayloadService
from pipe.core.factories.prompt_factory import PromptFactory
from pipe.core.models.args import TaktArgs
from pipe.core.models.unified_chunk import UnifiedChunk
from pipe.core.repositories.streaming_log_repository import StreamingLogRepository
from pipe.core.services.gemini_tool_service import GeminiToolService
from pipe.core.utils.datetime import get_current_datetime

if TYPE_CHECKING:
    from pipe.core.services.session_service import SessionService


@register_agent("gemini-api")
class GeminiApiAgent(BaseAgent):
    """
    Agent for Gemini API streaming mode.

    Responsibilities:
    - Build and render prompts (4-layer architecture for caching)
    - Load tools via ToolService
    - Manage cache via gemini_cache_utils
    - Execute API streaming calls
    - Log streaming chunks using StreamingLogRepository

    Note:
        This agent orchestrates the API call flow but delegates
        specific concerns to specialized domain classes and services.
    """

    def __init__(
        self,
        session_service: "SessionService",
        tool_service: GeminiToolService | None = None,
        payload_builder: GeminiApiPayloadBuilder | None = None,
    ):
        """
        Initialize the Gemini API agent.

        Args:
            session_service: Session service (required)
            tool_service: Optional tool service (default: GeminiToolService)
            payload_builder: Optional payload builder (default: GeminiApiPayloadBuilder)
        """
        self.session_service = session_service
        self.settings = session_service.settings
        self.project_root = session_service.project_root

        # Initialize sub-services with DI support
        self.tool_service = tool_service or GeminiToolService()
        self.payload_builder = payload_builder or GeminiApiPayloadBuilder(
            self.project_root, self.settings
        )

        # Initialize new payload service and prompt factory
        self.payload_service = GeminiPayloadService(
            client=genai.Client(),
            project_root=self.project_root,
            settings=self.settings,
        )
        self.prompt_factory = PromptFactory(
            project_root=self.project_root,
            resource_repository=session_service.repository,
        )

        # Initialize tokenizer
        self.tokenizer = gemini_token_count.create_local_tokenizer(
            self.settings.model.name
        )
        self.model_name = self.settings.model.name
        self.context_limit = self.settings.model.context_limit

        # Initialize other fields
        self.last_raw_response: str | None = None

        try:
            self.timezone = zoneinfo.ZoneInfo(self.settings.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            self.timezone = zoneinfo.ZoneInfo("UTC")

        self.last_cached_turn_count: int | None = None

    def run(
        self,
        args: TaktArgs,
        session_service: "SessionService",
    ) -> tuple[str, int | None, list, str | None]:
        """Execute the Gemini API agent.

        This wraps the streaming call and returns the final result
        after all streaming is complete.

        Args:
            args: Command line arguments
            session_service: Service for session management

        Returns:
            Tuple of (response_text, token_count, turns_to_save, thought_text)
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_api_delegate
        from pipe.core.services.session_turn_service import SessionTurnService

        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )
        stream_results = list(
            gemini_api_delegate.run_stream(args, session_service, session_turn_service)
        )
        # The last yielded item contains the final result
        (
            _,
            model_response_text,
            token_count,
            turns_to_save,
            model_response_thought,
        ) = stream_results[-1]

        return model_response_text, token_count, turns_to_save, model_response_thought

    def run_stream(
        self,
        args: TaktArgs,
        session_service: "SessionService",
    ):
        """Execute the Gemini API agent in streaming mode.

        This method yields intermediate results for WebUI streaming support.

        Args:
            args: Command line arguments
            session_service: Service for session management

        Yields:
            Intermediate streaming results and final tuple
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_api_delegate
        from pipe.core.services.session_turn_service import SessionTurnService

        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )
        yield from gemini_api_delegate.run_stream(
            args, session_service, session_turn_service
        )

    def stream_content(self) -> Generator[UnifiedChunk, None, None]:
        """
        Execute Gemini API call with streaming.

        Flow (New architecture with GeminiPayloadService):
        1. Prepare request with cache management (GeminiPayloadService)
        2. Load tools
        3. Log cache decision
        4. Execute streaming call

        Yields:
            Pydantic UnifiedChunk instances (TextChunk | ToolCallChunk | MetadataChunk)

        Raises:
            ValueError: If prompt exceeds token limit
            RuntimeError: If API call fails
        """
        session_data = self.session_service.current_session
        os.environ["PIPE_SESSION_ID"] = session_data.session_id

        # 0. Initialize token summary from session data if not yet set
        # This ensures cache decisions use current session state, not stale initial values
        if self.payload_service.last_token_summary["buffered_tokens"] == 0:
            self.payload_service.update_token_summary(
                {
                    "cached_content_token_count": session_data.cached_content_token_count,
                    "prompt_token_count": session_data.token_count,
                }
            )

        # 1. Prepare request payload with cache management
        contents, cache_name = self.payload_service.prepare_request(
            session=session_data,
            prompt_factory=self.prompt_factory,
            current_instruction=None,  # No new instruction in stream_content
        )

        # Store cached turn count from session (updated by payload_service)
        self.last_cached_turn_count = session_data.cached_turn_count

        # 2. Load tools
        loaded_tools = self.tool_service.load_tools(self.project_root)
        tools = self.tool_service.convert_to_genai_tools(loaded_tools)

        # 3. Log cache decision
        self._log_cache_decision(
            session_data,
            cache_name,
            self.payload_service.last_token_summary["buffered_tokens"],
        )

        # 4. Build generation config
        config = self._build_generation_config(
            session_data=session_data,
            cached_content_name=cache_name,
            converted_tools=tools,
        )

        # 5. Execute streaming call
        client = genai.Client()
        yield from self._execute_streaming_call(
            client=client,
            content_to_send=contents,
            config=config,
            session_data=session_data,
        )

    def _log_cache_decision(
        self, session_data, cache_name: str | None, buffered_tokens: int
    ) -> None:
        """
        Log cache decision to streaming log.

        Args:
            session_data: Current session data
            cache_name: Cache name if using cache, None otherwise
            buffered_tokens: Number of buffered tokens (not in cache)
        """
        streaming_log_repo = StreamingLogRepository(
            self.project_root, session_data.session_id, self.settings
        )
        streaming_log_repo.open(mode="a")

        try:
            threshold = self.settings.model.cache_update_threshold

            # Get turn counts
            cached_turn_count = session_data.cached_turn_count
            total_turns = len(session_data.turns)
            buffered_turn_count = total_turns - cached_turn_count

            # Build turn count info string
            turn_info = f"Static({cached_turn_count} turns), Buffered({buffered_turn_count} turns)"

            if cache_name:
                # Check if this is a new cache or using existing
                if buffered_tokens >= threshold:
                    # Case 1: Cache Update (Creation/Recreation)
                    cache_msg = (
                        f"Cache decision: CREATING/UPDATING cache (key={cache_name}). "
                        f"Current cached_tokens={session_data.cached_content_token_count}, "
                        f"Current prompt_tokens={session_data.token_count}, "
                        f"Buffered tokens={buffered_tokens}. "
                        f"{turn_info}"
                    )
                else:
                    # Case 2: Using Existing Cache (No Update)
                    cache_msg = (
                        f"Cache decision: USING EXISTING cache (key={cache_name}). "
                        f"Current cached_tokens={session_data.cached_content_token_count}, "
                        f"Current prompt_tokens={session_data.token_count}, "
                        f"Buffered tokens={buffered_tokens}, "
                        f"Threshold={threshold}. "
                        f"{turn_info}"
                    )
            else:
                # No cache
                if session_data.cached_content_token_count > 0:
                    # Case 4: No Cache (Empty Static Content)
                    cache_msg = (
                        f"Cache decision: NO CACHE (static.cached_content is empty). "
                        f"Current cached_tokens={session_data.cached_content_token_count}, "
                        f"Current prompt_tokens={session_data.token_count}, "
                        f"Buffered tokens={buffered_tokens}. "
                        f"{turn_info}"
                    )
                else:
                    # Case 3: No Cache (Below Threshold)
                    cache_msg = (
                        f"Cache decision: NO CACHE (below threshold). "
                        f"Current prompt_tokens={session_data.token_count}, "
                        f"Threshold={threshold}. "
                        f"Sending static + dynamic content. "
                        f"{turn_info}"
                    )

            streaming_log_repo.write_log_line(
                "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
            )
        finally:
            streaming_log_repo.close()

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

        try:
            stream = client.models.generate_content_stream(
                contents=content_to_send,
                config=config,
                model=self.model_name,
            )

            # Use stream processor to handle chunk processing and logging
            stream_processor = GeminiApiStreamProcessor(
                streaming_log_repo=raw_chunk_repo,
                timezone=self.timezone,
            )

            yield from stream_processor.process_stream(stream)

            # Save the last raw response for thought signature
            self.last_raw_response = stream_processor.get_last_raw_response()

        except Exception as e:
            raise RuntimeError(f"Error during Gemini API execution: {e}")
        finally:
            raw_chunk_repo.close()
