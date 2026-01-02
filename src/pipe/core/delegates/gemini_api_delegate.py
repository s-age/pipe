import json
import os

from pipe.cli.mcp_server import execute_tool
from pipe.core.agents.gemini_api import GeminiApiAgent
from pipe.core.models.turn import ModelResponseTurn
from pipe.core.models.unified_chunk import MetadataChunk, TextChunk, ToolCallChunk
from pipe.core.repositories.streaming_log_repository import StreamingLogRepository
from pipe.core.services.session_service import SessionService
from pipe.core.services.session_turn_service import SessionTurnService
from pipe.core.utils.datetime import get_current_timestamp


def run_stream(
    args,
    session_service: SessionService,
    session_turn_service: SessionTurnService,
):
    """Streaming version for web UI."""
    model_response_text = ""
    model_response_thought = ""
    token_count = 0
    prompt_token_count_for_cache = 0  # Track prompt tokens for cache decisions
    intermediate_turns = []
    tool_call_count = 0
    last_cached_content_token_count = (
        None  # Track last response's cache count (from final chunk)
    )

    settings = session_service.settings
    max_tool_calls = settings.max_tool_calls
    session_data = session_service.current_session
    session_id = session_service.current_session_id
    timezone_obj = session_service.timezone_obj

    previous_cached_content_token_count = (
        session_data.cached_content_token_count
    )  # Track previous cache count for delta calculation

    # Ensure PIPE_SESSION_ID is set for mcp_server
    os.environ["PIPE_SESSION_ID"] = session_id

    # Initialize streaming log repository for tee-style logging
    streaming_log_repo = StreamingLogRepository(
        project_root=session_service.project_root,
        session_id=session_id,
        settings=settings,
    )

    # Create GeminiApiAgent ONCE outside the loop to preserve payload_service state
    gemini_agent = GeminiApiAgent(session_service)

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

        # Update session_service reference in agent (session may have been reloaded)
        gemini_agent.session_service = session_service
        stream = gemini_agent.stream_content()

        full_text_parts = []
        thought_parts = []
        usage_metadata = None
        tool_call_chunk = None

        for unified_chunk in stream:
            if isinstance(unified_chunk, TextChunk):
                # Stream text content to user
                yield unified_chunk.content
                if unified_chunk.is_thought:
                    thought_parts.append(unified_chunk.content)
                else:
                    full_text_parts.append(unified_chunk.content)

            elif isinstance(unified_chunk, ToolCallChunk):
                # Store tool call for processing
                tool_call_chunk = unified_chunk

            elif isinstance(unified_chunk, MetadataChunk):
                # Store usage metadata
                usage_metadata = unified_chunk.usage

                # Update GeminiApiPayload with token summary
                if usage_metadata:
                    gemini_agent.payload_service.update_token_summary(
                        {
                            "cached_content_token_count": usage_metadata.cached_content_token_count
                            or 0,
                            "prompt_token_count": usage_metadata.prompt_token_count
                            or 0,
                        }
                    )

        # Check if we received actual content (text, thought, or tool)
        has_content = bool(full_text_parts or tool_call_chunk or thought_parts)

        if not usage_metadata and not has_content:
            yield "API Error: Model stream was empty."
            model_response_text = "API Error: Model stream was empty."
            break

        # Accumulate thought and text
        model_response_thought = "".join(thought_parts)
        model_response_text = "".join(full_text_parts)

        # If no content but usage reported, yield fallback message
        if usage_metadata and not has_content:
            fallback_msg = "\n(Model consumed tokens but generated no output. This may be a model refusal or internal stop.)"
            yield fallback_msg
            # Update text so it's not empty in the final turn
            model_response_text = fallback_msg

        # If text is empty but thought exists, yield a fallback message for visibility
        elif not model_response_text and model_response_thought:
            yield "\n(Model generated thoughts only. Check logs for details.)"

        # Extract token counts from metadata
        token_count = 0
        prompt_token_count_for_cache = 0
        if usage_metadata:
            prompt_tokens = usage_metadata.prompt_token_count or 0
            candidate_tokens = usage_metadata.candidates_token_count or 0
            total_tokens = usage_metadata.total_token_count or 0

            # Track the last cached_content_token_count from the stream
            # Note: We'll save this at the end, not during the loop
            cached_count = usage_metadata.cached_content_token_count
            if cached_count is None:
                last_cached_content_token_count = 0
            else:
                last_cached_content_token_count = cached_count

            # Calculate cache delta (increase in cached tokens)
            cache_delta = 0
            if (
                cached_count is not None
                and previous_cached_content_token_count is not None
            ):
                cache_delta = cached_count - previous_cached_content_token_count
                # Update previous for next iteration
                previous_cached_content_token_count = cached_count

            # token_count: Complete total for this API call (includes thoughts for billing/stats)
            # Subtract cache_delta to get actual conversation growth
            raw_total_tokens = (
                total_tokens if total_tokens else (prompt_tokens + candidate_tokens)
            )
            token_count = raw_total_tokens - cache_delta

            # prompt_token_count_for_cache: Tokens that will be in next prompt
            # (excludes thoughts since they're not part of conversation history)
            prompt_token_count_for_cache = prompt_tokens + candidate_tokens

            # Update cumulative token stats in session
            session = session_service.get_session(session_id)
            if session:
                # Add raw_total_tokens (includes prompt + candidates + thoughts) to cumulative counter
                # Note: We use raw_total_tokens here to maintain consistency with the original behavior
                cached_tokens = cached_count or 0
                session.cumulative_total_tokens += raw_total_tokens
                session.cumulative_cached_tokens += cached_tokens
                session_service.repository.save(session)

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
            # Final text response already set
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

            # Determine status and message for both logging and payload service
            if (
                isinstance(tool_result, dict)
                and "error" in tool_result
                and tool_result["error"] is not None
            ):
                status = "failed"
                output = str(tool_result["error"])
            else:
                status = "succeeded"
                if isinstance(tool_result, dict):
                    output = tool_result.get("message", str(tool_result))
                else:
                    output = str(tool_result)

            # Log tool result to streaming log
            if streaming_log_repo:
                truncated_output = f"{output[:200]}..." if len(output) > 200 else output
                log_content = (
                    f"TOOL_RESULT: {function_call.name} | status: {status} | "
                    f"output: {truncated_output}"
                )
                streaming_log_repo.append_log(log_content, "TOOL_RESULT")

            # Update the FunctionCallingTurn in the pool with raw_response
            # (contains thought signature)
            if gemini_agent.last_raw_response:
                # Reload session to get the pool updated by execute_tool
                session = session_service.repository.find(session_id)
                if session and session.pools:
                    # Find the last FunctionCallingTurn in the pool
                    for turn in reversed(session.pools):
                        if turn.type == "function_calling":
                            turn.raw_response = gemini_agent.last_raw_response
                            session_service.repository.save(session)
                            break

        except Exception as e:
            tool_result = {"error": str(e)}

            # Log tool error to streaming log
            if streaming_log_repo:
                error_msg = str(e)
                truncated_error = (
                    f"{error_msg[:200]}..." if len(error_msg) > 200 else error_msg
                )
                log_content = (
                    f"TOOL_RESULT: {function_call.name} | status: failed | "
                    f"output: {truncated_error}"
                )
                streaming_log_repo.append_log(log_content, "TOOL_RESULT")

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
        thought=model_response_thought if model_response_thought else None,
        timestamp=get_current_timestamp(timezone_obj),
        raw_response=gemini_agent.last_raw_response if gemini_agent else None,
    )
    intermediate_turns.append(final_model_turn)

    # Update token count and cached content token count at the end
    # Use the last values from the final chunk of the last API call
    if prompt_token_count_for_cache > 0:
        from pipe.core.services.session_meta_service import SessionMetaService

        session_meta_service = SessionMetaService(session_service.repository)
        session_meta_service.update_token_count(
            session_id, prompt_token_count_for_cache
        )

        # Update cached_content_token_count from the LAST chunk of the stream
        # This is critical: we use the final value, not the first one
        # None means we haven't received any response yet (first iteration)
        if last_cached_content_token_count is not None:
            session_meta_service.update_cached_content_token_count(
                session_id, last_cached_content_token_count
            )

        # Update cached_turn_count using the value from the agent
        if gemini_agent and gemini_agent.last_cached_turn_count is not None:
            session_meta_service.update_cached_turn_count(
                session_id, gemini_agent.last_cached_turn_count
            )

    # Cleanup streaming.log after model response is complete
    streaming_log_repo = StreamingLogRepository(
        session_service.project_root, session_id, settings
    )
    streaming_log_repo.delete()

    # Return final data
    yield (
        "end",
        model_response_text,
        token_count,
        intermediate_turns,
        model_response_thought,
    )
