import json
import os

from pipe.cli.mcp_server import execute_tool
from pipe.core.models.turn import (
    ModelResponseTurn,
)
from pipe.core.models.unified_chunk import MetadataChunk, TextChunk, ToolCallChunk
from pipe.core.repositories.streaming_repository import StreamingRepository
from pipe.core.services.gemini_client_service import GeminiClientService
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService
from pipe.core.services.session_turn_service import SessionTurnService
from pipe.core.utils.datetime import get_current_timestamp


def run_stream(
    args,
    session_service: SessionService,
    prompt_service: PromptService,
    session_turn_service: SessionTurnService,
):
    """Streaming version for web UI."""
    model_response_text = ""
    token_count = 0
    prompt_token_count_for_cache = 0  # Track prompt tokens for cache decisions
    intermediate_turns = []
    tool_call_count = 0
    first_cached_content_token_count = None  # Track first response's cache count

    settings = session_service.settings
    max_tool_calls = settings.max_tool_calls
    session_data = session_service.current_session
    session_id = session_service.current_session_id
    timezone_obj = session_service.timezone_obj

    # Ensure PIPE_SESSION_ID is set for mcp_server
    os.environ["PIPE_SESSION_ID"] = session_id

    while tool_call_count < max_tool_calls:
        session_turn_service.merge_pool_into_turns(session_id)

        # Reload session to ensure we have the latest turns and file changes
        reloaded_session = session_service.get_session(session_id)
        if reloaded_session:
            session_service.current_session = reloaded_session
            session_data = session_service.current_session

        # Update session with latest token counts BEFORE calling API
        # This ensures cache decisions are made with fresh data from previous response
        # Skip on first iteration (no previous response yet)
        # Use prompt_token_count (not total) for cache decisions
        if prompt_token_count_for_cache > 0:
            from pipe.core.services.session_meta_service import SessionMetaService

            session_meta_service = SessionMetaService(session_service.repository)
            session_meta_service.update_token_count(
                session_id, prompt_token_count_for_cache
            )

            # Reload session after token count update
            reloaded_session = session_service.get_session(session_id)
            if reloaded_session:
                session_service.current_session = reloaded_session
                session_data = session_service.current_session

        # Use GeminiClientService with unified Pydantic chunk format
        gemini_client = GeminiClientService(session_service)
        stream = gemini_client.stream_content(prompt_service)

        full_text_parts = []
        usage_metadata = None
        tool_call_chunk = None

        for unified_chunk in stream:
            if isinstance(unified_chunk, TextChunk):
                # Stream text content to user
                yield unified_chunk.content
                full_text_parts.append(unified_chunk.content)

            elif isinstance(unified_chunk, ToolCallChunk):
                # Store tool call for processing
                tool_call_chunk = unified_chunk

            elif isinstance(unified_chunk, MetadataChunk):
                # Store usage metadata
                usage_metadata = unified_chunk.usage

        if not usage_metadata and not full_text_parts and not tool_call_chunk:
            yield "API Error: Model stream was empty."
            model_response_text = "API Error: Model stream was empty."
            break

        # Extract token counts from metadata
        token_count = 0
        prompt_token_count_for_cache = 0
        if usage_metadata:
            prompt_tokens = usage_metadata.prompt_token_count or 0
            candidate_tokens = usage_metadata.candidates_token_count or 0
            token_count = prompt_tokens + candidate_tokens
            prompt_token_count_for_cache = prompt_tokens

            # Capture cached_content_token_count from the first response only
            cached_count = usage_metadata.cached_content_token_count
            if first_cached_content_token_count is None and cached_count is not None:
                first_cached_content_token_count = cached_count

                # Update session with first response's cached count immediately
                from pipe.core.services.session_meta_service import SessionMetaService

                session_meta_service = SessionMetaService(session_service.repository)
                session_meta_service.update_cached_content_token_count(
                    session_id, first_cached_content_token_count
                )

                # Reload session after cache count update
                reloaded_session = session_service.get_session(session_id)
                if reloaded_session:
                    session_service.current_session = reloaded_session
                    session_data = session_service.current_session

        # Check if we have a tool call
        function_call = None
        if tool_call_chunk:
            # Create a simple object to mimic the old function_call structure
            class FunctionCall:
                def __init__(self, name, args):
                    self.name = name
                    self.args = args

            function_call = FunctionCall(tool_call_chunk.name, tool_call_chunk.args)

        if not function_call:
            model_response_text = "".join(full_text_parts)
            break

        tool_call_count += 1
        if tool_call_count >= max_tool_calls:
            yield "Error: Maximum number of tool calls reached. Halting execution."
            model_response_text = (
                "Error: Maximum number of tool calls reached. Halting execution."
            )
            break

        args_json_string_for_display = json.dumps(
            dict(function_call.args), ensure_ascii=False, indent=2
        )
        tool_call_markdown = (
            f"```\nTool call: {function_call.name}\nArgs:\n"
            f"{args_json_string_for_display}\n```\n"
        )
        yield tool_call_markdown

        # Note: execute_tool from mcp_server handles adding FunctionCallingTurn to pool

        try:
            tool_result = execute_tool(function_call.name, dict(function_call.args))
        except Exception as e:
            tool_result = {"error": str(e)}

        reloaded_session = session_service.get_session(session_id)
        if reloaded_session:
            session_data.references = reloaded_session.references
            session_data.todos = reloaded_session.todos
            session_data.hyperparameters = reloaded_session.hyperparameters

        if (
            isinstance(tool_result, dict)
            and "error" in tool_result
            and tool_result["error"] is not None
        ):
            formatted_response = {"status": "failed", "message": tool_result["error"]}
        else:
            # Handle different successful tool return formats
            if isinstance(tool_result, dict):
                formatted_response = tool_result.copy()
                formatted_response["status"] = "succeeded"
                if "message" not in formatted_response:
                    formatted_response["message"] = formatted_response.get(
                        "content", str(tool_result)
                    )
            else:
                formatted_response = {"status": "succeeded", "message": tool_result}

        status_markdown = f"```\nTool status: {formatted_response['status']}\n```\n"
        yield status_markdown

        # Note: execute_tool from mcp_server handles adding ToolResponseTurn to pool

    final_model_turn = ModelResponseTurn(
        type="model_response",
        content=model_response_text,
        timestamp=get_current_timestamp(timezone_obj),
    )
    intermediate_turns.append(final_model_turn)

    if gemini_client.last_raw_response:
        session_turn_service.update_raw_response(
            session_id, gemini_client.last_raw_response
        )

    # Update token count and cached content token count
    if prompt_token_count_for_cache > 0:
        from pipe.core.services.session_meta_service import SessionMetaService

        session_meta_service = SessionMetaService(session_service.repository)
        session_meta_service.update_token_count(
            session_id, prompt_token_count_for_cache
        )

        # Update cached_content_token_count from first API response only
        if first_cached_content_token_count is not None:
            session_meta_service.update_cached_content_token_count(
                session_id, first_cached_content_token_count
            )

    # Cleanup streaming.log after model response is complete
    sessions_dir = os.path.join(session_service.project_root, "sessions")
    streaming_repo = StreamingRepository(sessions_dir)
    streaming_repo.cleanup(session_id)

    # Return final data
    yield ("end", model_response_text, token_count, intermediate_turns)
