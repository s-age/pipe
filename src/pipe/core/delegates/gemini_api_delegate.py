import json
import os

from pipe.cli.mcp_server import execute_tool
from pipe.core.agents.gemini_api import call_gemini_api
from pipe.core.models.turn import (
    ModelResponseTurn,
)
from pipe.core.repositories.streaming_repository import StreamingRepository
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
    intermediate_turns = []
    tool_call_count = 0

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

        stream = call_gemini_api(session_service, prompt_service)

        response_chunks = []
        full_text_parts = []
        for chunk in stream:
            # Correctly iterate through parts to find text for streaming
            if (
                chunk.candidates
                and chunk.candidates[0].content
                and chunk.candidates[0].content.parts
            ):
                for part in chunk.candidates[0].content.parts:
                    if part.text:
                        yield part.text
                        full_text_parts.append(part.text)
            response_chunks.append(chunk)

        if not response_chunks:
            yield "API Error: Model stream was empty."
            model_response_text = "API Error: Model stream was empty."
            break

        final_response = response_chunks[-1]
        full_text = "".join(full_text_parts)
        if (
            final_response.candidates
            and final_response.candidates[0].content
            and final_response.candidates[0].content.parts
        ):
            # This is to ensure the final response object has the complete text,
            # though the primary text source is now full_text_parts.
            final_response.candidates[0].content.parts[0].text = full_text

        response = final_response
        token_count = 0
        if response.usage_metadata:
            prompt_tokens = response.usage_metadata.prompt_token_count or 0
            candidate_tokens = response.usage_metadata.candidates_token_count or 0
            token_count = prompt_tokens + candidate_tokens

        if not response.candidates:
            yield "API Error: No candidates in response."
            model_response_text = "API Error: No candidates in response."
            break

        function_call = None
        try:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_call = part.function_call
                    break
        except (IndexError, AttributeError):
            function_call = None

        if not function_call:
            model_response_text = full_text
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
            and tool_result["error"] != "(none)"
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

    # Update token count
    if token_count > 0:
        from pipe.core.services.session_meta_service import SessionMetaService

        session_meta_service = SessionMetaService(session_service.repository)
        session_meta_service.update_token_count(session_id, token_count)

    # Cleanup streaming.log after model response is complete
    sessions_dir = os.path.join(session_service.project_root, "sessions")
    streaming_repo = StreamingRepository(sessions_dir)
    streaming_repo.cleanup(session_id)

    # Return final data
    yield ("end", model_response_text, token_count, intermediate_turns)
