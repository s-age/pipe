import json

from pipe.core.agents.gemini_cli import call_gemini_cli
from pipe.core.domains import gemini_token_count
from pipe.core.domains.gemini_cli_payload import GeminiCliPayloadBuilder
from pipe.core.domains.gemini_cli_stream_processor import StreamResult
from pipe.core.models.args import TaktArgs
from pipe.core.services.gemini_tool_service import GeminiToolService
from pipe.core.services.session_service import SessionService
from pipe.core.services.session_turn_service import SessionTurnService


def _reconcile_tool_calls(
    stream_result: StreamResult,
    session_service: SessionService,
) -> None:
    """
    Reconcile tool calls from two sources after subprocess completes:
    1. mcp_server.py: Wrote pipe_tools to session.pools (via MCP protocol)
    2. stream_result: Contains standard tools from gemini-cli's JSON stdout

    Strategy:
    - Reload session from disk (mcp_server modified it during subprocess)
    - If pools is empty: mcp_server didn't run → add standard tools from stream
    - If pools has data: mcp_server ran → skip (already recorded)

    This runs AFTER gemini-cli subprocess finishes, so no concurrent file access.
    """
    from pipe.core.models.turn import (
        FunctionCallingTurn,
        ToolResponseTurn,
        TurnResponse,
    )
    from pipe.core.utils.datetime import get_current_timestamp

    session_id = session_service.current_session_id
    if not session_id:
        return

    # CRITICAL: Reload session from disk to get mcp_server's writes
    session = session_service.get_session(session_id)
    if not session:
        import sys

        print(
            f"Warning: Session {session_id} not found during tool reconciliation",
            file=sys.stderr,
        )
        return

    # If pools is not empty, mcp_server already recorded tool calls (pipe_tools)
    if len(session.pools) != 0:
        return

    # If pools is empty, add standard tools from stream
    if not (stream_result.tool_calls or stream_result.tool_results):
        return

    # Add tool calls from stream
    for tool_call in stream_result.tool_calls:
        tool_name = tool_call.get("tool_name", "")
        parameters = tool_call.get("parameters", {})
        params_json = json.dumps(parameters, ensure_ascii=False)
        response_str = f"{tool_name}({params_json})"
        timestamp = tool_call.get(
            "timestamp",
            get_current_timestamp(session_service.timezone_obj),
        )
        turn = FunctionCallingTurn(
            type="function_calling",
            response=response_str,
            timestamp=timestamp,
        )
        session.pools.append(turn)

    # Add tool results from stream
    for tool_result in stream_result.tool_results:
        tool_name = tool_result.get("tool_id", "").split("-")[0]
        status = tool_result.get("status", "failed")
        output = tool_result.get("output", "")
        error = tool_result.get("error")

        if status == "success":
            response = TurnResponse(status="succeeded", message=output)
        else:
            if isinstance(error, dict):
                error_msg = error.get("message", "")
            else:
                error_msg = str(error)
            response = TurnResponse(status="failed", message=error_msg)

        timestamp = tool_result.get(
            "timestamp",
            get_current_timestamp(session_service.timezone_obj),
        )
        turn = ToolResponseTurn(
            type="tool_response",
            name=tool_name,
            response=response,
            timestamp=timestamp,
        )
        session.pools.append(turn)

    # Save updated session
    session_service.repository.save(session)


def run(
    args: TaktArgs,
    session_service: SessionService,
    session_turn_service: SessionTurnService,
) -> tuple[str, int, dict | None]:
    """
    Handles the logic for the 'gemini-cli' mode by delegating to call_gemini_cli.
    This function is now only responsible for getting the model's response text.
    """
    # Build the prompt once using GeminiCliPayloadBuilder
    # This prompt will be used for both token counting and the API call
    payload_builder = GeminiCliPayloadBuilder(
        project_root=session_service.project_root,
        api_mode=session_service.settings.api_mode,
    )
    rendered_prompt = payload_builder.build(session_service)

    # Calculate token count from the complete prompt (including all turns)
    # Load tools
    tool_service = GeminiToolService()
    tools = tool_service.load_tools(session_service.project_root)

    # Create tokenizer and count tokens
    tokenizer = gemini_token_count.create_local_tokenizer(
        session_service.settings.model.name
    )
    token_count = gemini_token_count.count_tokens(
        rendered_prompt, tools=tools, tokenizer=tokenizer
    )

    # Call gemini-cli subprocess
    result = call_gemini_cli(
        session_service, args.output_format, prompt=rendered_prompt
    )
    response_text = result.response  # StreamResult.response instead of dict
    stats = result.stats

    # CRITICAL: Reload session and reconcile tool calls
    # (mcp_server may have written to pools during subprocess execution)
    if session_service.current_session_id:
        session_service.current_session = session_service.get_session(
            session_service.current_session_id
        )
        _reconcile_tool_calls(result, session_service)
        session_turn_service.merge_pool_into_turns(session_service.current_session_id)

    return response_text, token_count, stats
