import importlib
import inspect
import json
import sys

from pipe.core.agents.gemini_api import call_gemini_api
from pipe.core.models.turn import (
    FunctionCallingTurn,
    ModelResponseTurn,
    ToolResponseTurn,
)
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService
from pipe.core.utils.datetime import get_current_timestamp


def execute_tool_call(tool_call, session_service, session_id, settings, project_root):
    """Dynamically imports and executes a tool function, passing context if needed."""
    tool_name = tool_call.name
    tool_args = dict(tool_call.args)

    try:
        tool_module = importlib.import_module(f"pipe.core.tools.{tool_name}")
        importlib.reload(tool_module)

        tool_function = getattr(tool_module, tool_name)

        sig = inspect.signature(tool_function)
        params = sig.parameters

        final_args = tool_args.copy()

        if "session_service" in params:
            final_args["session_service"] = session_service
        if "session_id" in params and "session_id" not in tool_args:
            final_args["session_id"] = session_id
        if "settings" in params:
            final_args["settings"] = settings
        if "project_root" in params:
            final_args["project_root"] = project_root

        result = tool_function(**final_args)
        return result
    except Exception as e:
        import traceback

        print(f"--- ERROR during tool execution: {tool_name} ---", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        print("-------------------------------------------------", file=sys.stderr)
        return {"error": f"Failed to execute tool {tool_name}: {e}"}


def run_stream(args, session_service: SessionService, prompt_service: PromptService):
    """Streaming version for web UI."""
    model_response_text = ""
    token_count = 0
    intermediate_turns = []
    tool_call_count = 0

    settings = session_service.settings
    max_tool_calls = settings.max_tool_calls
    session_data = session_service.current_session
    project_root = session_service.project_root
    session_id = session_service.current_session_id
    timezone_obj = session_service.timezone_obj

    while tool_call_count < max_tool_calls:
        session_service.merge_pool_into_turns(session_id)
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

        response_string = (
            f"{function_call.name}("
            f"{json.dumps(dict(function_call.args), ensure_ascii=False)})"
        )

        model_turn = FunctionCallingTurn(
            type="function_calling",
            response=response_string,
            timestamp=get_current_timestamp(timezone_obj),
        )

        tool_result = execute_tool_call(
            function_call, session_service, session_id, settings, project_root
        )

        reloaded_session = session_service.get_session(session_id)
        if reloaded_session:
            session_data.references = reloaded_session.references

        if (
            isinstance(tool_result, dict)
            and "error" in tool_result
            and tool_result["error"] != "(none)"
        ):
            formatted_response = {"status": "failed", "message": tool_result["error"]}
        else:
            # Handle different successful tool return formats
            if isinstance(tool_result, dict):
                message_content = tool_result.get(
                    "message", tool_result.get("content", tool_result)
                )
            else:
                message_content = tool_result
            formatted_response = {"status": "succeeded", "message": message_content}

        status_markdown = f"```\nTool status: {formatted_response['status']}\n```\n"
        yield status_markdown

        tool_turn = ToolResponseTurn(
            type="tool_response",
            name=function_call.name,
            response=formatted_response,
            timestamp=get_current_timestamp(timezone_obj),
        )
        intermediate_turns.append(model_turn)
        intermediate_turns.append(tool_turn)
        session_data.turns.append(model_turn)
        session_data.turns.append(tool_turn)

    final_model_turn = ModelResponseTurn(
        type="model_response",
        content=model_response_text,
        timestamp=get_current_timestamp(timezone_obj),
    )
    intermediate_turns.append(final_model_turn)

    # Return final data
    yield ("end", model_response_text, token_count, intermediate_turns)
