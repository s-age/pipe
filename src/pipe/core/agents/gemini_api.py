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
from pipe.core.domains.gemini_api_cache import GeminiApiCacheManager
from pipe.core.domains.gemini_api_payload import GeminiApiPayloadBuilder
from pipe.core.domains.gemini_api_stream_processor import GeminiApiStreamProcessor
from pipe.core.domains.gemini_cache import GeminiCache
from pipe.core.models.args import TaktArgs
from pipe.core.models.unified_chunk import UnifiedChunk
from pipe.core.repositories.streaming_log_repository import StreamingLogRepository
from pipe.core.services.gemini_tool_service import GeminiToolService

if TYPE_CHECKING:
    from pipe.core.services.session_service import SessionService


@register_agent("gemini-api")
class GeminiApiAgent(BaseAgent):
    """
    Agent for Gemini API streaming mode.

    Responsibilities:
    - Build and render prompts (static/dynamic split for caching)
    - Load tools via ToolService
    - Manage cache via GeminiApiCacheManager
    - Execute API streaming calls
    - Log streaming chunks using StreamingLogRepository

    Note:
        This agent orchestrates the API call flow but delegates
        specific concerns to specialized domain classes and services.
    """

    def __init__(self, session_service: "SessionService"):
        """
        Initialize the Gemini API agent.

        Args:
            session_service: Session service for accessing session data and settings
        """
        self.session_service = session_service
        self.settings = session_service.settings
        self.project_root = session_service.project_root

        # Initialize sub-services and domain classes
        self.tool_service = GeminiToolService()
        self.cache_manager = GeminiApiCacheManager(self.project_root, self.settings)

        # Initialize tokenizer for token counting
        self.tokenizer = gemini_token_count.create_local_tokenizer(
            self.settings.model.name
        )
        self.model_name = self.settings.model.name
        self.context_limit = self.settings.model.context_limit

        self.payload_builder = GeminiApiPayloadBuilder(self.project_root, self.settings)
        self.last_raw_response: str | None = None

        # Convert timezone string to ZoneInfo object
        try:
            self.timezone = zoneinfo.ZoneInfo(self.settings.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            # Fallback to UTC if timezone not found
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
        Execute Gemini API call with streaming and return UNIFIED CHUNKS.

        Flow:
        1. Build prompt model (PromptService)
        2. Render static/dynamic templates with payload builder
        3. Load tools (GeminiToolService)
        4. Check token limits (TokenService)
        5. Determine cache strategy (GeminiCache domain)
        6. Create/retrieve cache (GeminiApiCacheManager)
        7. Execute streaming API call
        8. Log chunks (StreamingLogRepository with append mode)
        9. Yield standardized Pydantic chunks (model-agnostic format)

        Unified Chunk Types:
            - TextChunk: Text content from model
            - ToolCallChunk: Tool call request
            - MetadataChunk: Usage metadata

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
        prompt_model = self.payload_builder.build_prompt(self.session_service)

        # 2. Render static and dynamic content
        static_content, dynamic_content = self.payload_builder.render(prompt_model)

        # 3. Prepare Buffered History as Content objects
        buffered_contents: list[types.Content] = []
        if prompt_model.buffered_history and prompt_model.buffered_history.turns:
            turns = prompt_model.buffered_history.turns

            for i, turn in enumerate(turns):
                # Use the turn's own raw_response if available
                content_obj = self.payload_builder.convert_turn_to_content(turn)
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
        token_count = gemini_token_count.count_tokens(
            full_text, tools=loaded_tools_data, tokenizer=self.tokenizer
        )

        is_within_limit, message = gemini_token_count.check_token_limit(
            token_count, self.context_limit
        )
        if not is_within_limit:
            raise ValueError("Prompt exceeds context window limit. Aborting.")

        # 7. Convert tools to Gemini types
        converted_tools = self.payload_builder.convert_tools(loaded_tools_data)

        # 8. Initialize API client
        client = genai.Client()

        # 9. Determine cache strategy and prepare content
        gemini_cache = GeminiCache(
            tool_response_limit=self.settings.tool_response_expiration,
            cache_update_threshold=self.settings.model.cache_update_threshold,
        )

        # Setup logging repository for cache decisions
        streaming_log_repo = StreamingLogRepository(
            self.project_root, session_data.session_id, self.settings
        )
        streaming_log_repo.open(mode="a")

        try:
            cached_content_name, content_to_send = (
                self.cache_manager.prepare_cache_and_content(
                    client=client,
                    gemini_cache=gemini_cache,
                    session_data=session_data,
                    static_content=static_content,
                    dynamic_content=dynamic_content,
                    converted_tools=converted_tools,
                    buffered_history_contents=buffered_contents,
                    current_task_content=current_task_content,
                    model_name=self.model_name,
                    streaming_log_repo=streaming_log_repo,
                )
            )
        finally:
            streaming_log_repo.close()

        # Capture the number of turns used in the cache if cache is active
        if (
            cached_content_name
            and prompt_model.cached_history
            and prompt_model.cached_history.turns
        ):
            self.last_cached_turn_count = len(prompt_model.cached_history.turns)
        else:
            self.last_cached_turn_count = 0

        # 10. Build generation config
        config = self.payload_builder.build_generation_config(
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
