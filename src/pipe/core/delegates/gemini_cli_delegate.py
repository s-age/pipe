from typing import Any

from pipe.core.agents.gemini_cli import call_gemini_cli
from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService
from pipe.core.services.session_turn_service import SessionTurnService


def run(
    args: TaktArgs,
    session_service: SessionService,
    session_turn_service: SessionTurnService,
) -> tuple[str, int, dict | None]:
    """
    Handles the logic for the 'gemini-cli' mode by delegating to call_gemini_cli.
    This function is now only responsible for getting the model's response text.
    """
    # Call the agent and return the response text.
    # The dispatcher will be responsible for creating and adding the turn.
    result = call_gemini_cli(session_service, args.output_format)
    response_text = result.get("response", "")
    stats = result.get("stats")
    token_count = 0
    if stats:
        # Calculate actual consumed tokens (not cumulative total_tokens)
        # Consumed = non-cached input tokens + output tokens
        input_tokens = stats.get("input_tokens", 0)
        cached_tokens = stats.get("cached", 0)
        output_tokens = stats.get("output_tokens", 0)

        # Actual consumption = input_tokens - cached_tokens + output_tokens
        # But if we don't have detailed stats, fall back to total_tokens
        if input_tokens > 0 or output_tokens > 0:
            non_cached_input = max(0, input_tokens - cached_tokens)
            token_count = non_cached_input + output_tokens
        elif "total_tokens" in stats:
            # Fallback to total_tokens if detailed stats not available
            token_count = stats.get("total_tokens", 0)
        # Fallback to old format with models
        elif "models" in stats:
            # Extract total tokens from the first model
            model_stats: dict[str, Any] = next(iter(stats["models"].values()), {})
            token_count = model_stats.get("tokens", {}).get("total", 0)

    # For stream-json, response_text is empty, collect from the streamed output
    if args.output_format == "stream-json":
        # The response is already streamed, collect the assistant messages
        # For simplicity, assume response_text is collected in call_gemini_cli
        pass

    # Merge any tool calls that occurred during the subprocess execution from the pool
    # into the main turns history before the final model response is added.
    if session_service.current_session_id:
        # CRITICAL: Reload the session from disk. The 'gemini' subprocess, running
        # mcp_server, has modified the session file by adding tool calls to the pool.
        # We must reload it here to get the latest state before merging.
        session_id = session_service.current_session_id
        session_service.current_session = session_service.get_session(session_id)

        session_turn_service.merge_pool_into_turns(session_id)

    return response_text, token_count, stats
