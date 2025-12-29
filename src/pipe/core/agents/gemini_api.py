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
from pipe.core.domains.gemini_cache import GeminiCache
from pipe.core.models.args import TaktArgs
from pipe.core.models.gemini_api_payload import (
    GeminiApiDynamicPayload,
    GeminiApiStaticPayload,
)
from pipe.core.models.unified_chunk import UnifiedChunk
from pipe.core.repositories.streaming_log_repository import StreamingLogRepository
from pipe.core.services.gemini_tool_service import GeminiToolService
from pipe.core.utils import gemini_cache_utils
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

        Flow (4-layer architecture):
        1. Build complete 4-layer payload (PayloadBuilder)
        2. Validate token limits
        3. Execute with cache
        4. Stream and process response (StreamProcessor)

        Yields:
            Pydantic UnifiedChunk instances (TextChunk | ToolCallChunk | MetadataChunk)

        Raises:
            ValueError: If prompt exceeds token limit
            RuntimeError: If API call fails
        """
        session_data = self.session_service.current_session
        os.environ["PIPE_SESSION_ID"] = session_data.session_id

        # 1. Build complete 4-layer payload
        loaded_tools = self.tool_service.load_tools(self.project_root)
        static, dynamic, tools = self.payload_builder.build_payloads_with_tools(
            self.session_service, loaded_tools
        )

        # Store cached turn count from payload builder
        self.last_cached_turn_count = self.payload_builder.last_cached_turn_count

        # 2. Validate token limits (use dict format for token counting)
        self._validate_context_limit(static, dynamic, loaded_tools)

        # 3. Execute with cache
        yield from self._execute_with_cache(static, dynamic, tools, session_data)

    def _validate_context_limit(
        self,
        static: GeminiApiStaticPayload,
        dynamic: GeminiApiDynamicPayload,
        tools_dict: list[dict],
    ) -> None:
        """Validate that payload doesn't exceed token limit.

        Args:
            static: Static payload
            dynamic: Dynamic payload
            tools_dict: Tool definitions in dict format (for token counting)
        """
        full_text = (static.cached_content or "") + dynamic.dynamic_content
        token_count = gemini_token_count.count_tokens(
            full_text, tools=tools_dict, tokenizer=self.tokenizer
        )

        is_within_limit, message = gemini_token_count.check_token_limit(
            token_count, self.context_limit
        )
        if not is_within_limit:
            raise ValueError("Prompt exceeds context window limit. Aborting.")

    def _execute_with_cache(
        self,
        static: GeminiApiStaticPayload,
        dynamic: GeminiApiDynamicPayload,
        tools: list[types.Tool],
        session_data,
    ) -> Generator[UnifiedChunk, None, None]:
        """Execute API call with cache management."""
        client = genai.Client()

        # Determine cache strategy
        gemini_cache = GeminiCache(
            tool_response_limit=self.settings.tool_response_expiration,
            cache_update_threshold=self.settings.model.cache_update_threshold,
        )

        buffered_tokens = (
            session_data.token_count - session_data.cached_content_token_count
            if session_data.cached_content_token_count > 0
            else session_data.token_count
        )
        should_cache = gemini_cache.should_update_cache(buffered_tokens)

        # Setup logging repository
        streaming_log_repo = StreamingLogRepository(
            self.project_root, session_data.session_id, self.settings
        )
        streaming_log_repo.open(mode="a")

        try:
            # Get or create cache if needed
            cached_content_name = None
            if should_cache and static.cached_content:
                cached_content_name = gemini_cache_utils.get_or_create_cache(
                    client,
                    static.cached_content,
                    self.model_name,
                    tools,
                    self.project_root,
                    session_data.session_id,
                    force_create=should_cache,
                )

                cache_msg = (
                    f"Cache decision: CREATING/UPDATING cache (key={cached_content_name}). "
                    f"Current cached_tokens={session_data.cached_content_token_count}, "
                    f"Current prompt_tokens={session_data.token_count}, "
                    f"Buffered tokens={buffered_tokens}"
                )
                streaming_log_repo.write_log_line(
                    "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
                )

            elif not session_data.cached_content_token_count:
                # No cache exists, below threshold
                cache_msg = (
                    f"Cache decision: NO CACHE (below threshold). "
                    f"Current prompt_tokens={session_data.token_count}, "
                    f"Threshold={gemini_cache.cache_update_threshold}. "
                    f"Sending static + dynamic content"
                )
                streaming_log_repo.write_log_line(
                    "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
                )

            else:
                # Use existing cache
                if static.cached_content:
                    try:
                        cached_content_name = gemini_cache_utils.get_or_create_cache(
                            client,
                            static.cached_content,
                            self.model_name,
                            tools,
                            self.project_root,
                            session_data.session_id,
                        )
                        cache_msg = (
                            f"Cache decision: USING EXISTING cache (key={cached_content_name}). "
                            f"Current cached_tokens={session_data.cached_content_token_count}, "
                            f"Current prompt_tokens={session_data.token_count}, "
                            f"Buffered tokens={buffered_tokens}, "
                            f"Threshold={gemini_cache.cache_update_threshold}"
                        )
                    except Exception as e:
                        cache_msg = (
                            f"Cache decision: FAILED to get cache (error={str(e)}). "
                            f"Current cached_tokens={session_data.cached_content_token_count}, "
                            f"Current prompt_tokens={session_data.token_count}, "
                            f"Buffered tokens={buffered_tokens}"
                        )
                else:
                    cache_msg = (
                        f"Cache decision: NO CACHE (static.cached_content is empty). "
                        f"Current cached_tokens={session_data.cached_content_token_count}, "
                        f"Current prompt_tokens={session_data.token_count}, "
                        f"Buffered tokens={buffered_tokens}"
                    )

                streaming_log_repo.write_log_line(
                    "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
                )

        finally:
            streaming_log_repo.close()

        # Build content list (4-layer ordering)
        content_to_send = self._build_content_list(
            static, dynamic, use_cache=(cached_content_name is not None)
        )

        # Build generation config
        config = self.payload_builder.build_generation_config(
            session_data=session_data,
            cached_content_name=cached_content_name,
            converted_tools=tools,
        )

        # Execute streaming call
        yield from self._execute_streaming_call(
            client=client,
            content_to_send=content_to_send,
            config=config,
            session_data=session_data,
        )

    def _build_content_list(
        self,
        static: GeminiApiStaticPayload,
        dynamic: GeminiApiDynamicPayload,
        use_cache: bool = False,
    ) -> list[types.Content | str]:
        """
        Build ordered content list for API transmission.

        Args:
            static: Static payload (Layers 1-2)
            dynamic: Dynamic payload (Layers 3-4)
            use_cache: If True, skip Layer 1 (use cache reference instead)

        Returns:
            Ordered list following 4-layer architecture:
            Layer 1 (Static): Cached content (skip if using cache)
            Layer 2 (Dynamic): Dynamic context
            Layer 3 (Buffered): Recent history
            Layer 4 (Trigger): Current instruction
        """
        content = []

        # Layer 1: Cached content (skip if using cache reference)
        if not use_cache and static.cached_content:
            content.append(static.cached_content)

        # Layer 2: Dynamic context
        content.append(dynamic.dynamic_content)

        # Layer 3: Buffered history
        content.extend(static.buffered_history)

        # Layer 4: Current instruction
        if dynamic.current_instruction:
            content.append(dynamic.current_instruction)

        return content

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
