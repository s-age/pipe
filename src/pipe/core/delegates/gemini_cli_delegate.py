from pipe.core.agents.gemini_cli import call_gemini_cli
from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService


def run(args: TaktArgs, session_service: SessionService) -> str:
    """
    Handles the logic for the 'gemini-cli' mode by delegating to call_gemini_cli.
    This function is now only responsible for getting the model's response text.
    """
    # Call the agent and return the response text.
    # The dispatcher will be responsible for creating and adding the turn.
    response_text = call_gemini_cli(session_service)

    # Merge any tool calls that occurred during the subprocess execution from the pool
    # into the main turns history before the final model response is added.
    if session_service.current_session_id:
        # CRITICAL: Reload the session from disk. The 'gemini' subprocess, running
        # mcp_server, has modified the session file by adding tool calls to the pool.
        # We must reload it here to get the latest state before merging.
        session_id = session_service.current_session_id
        session_service.current_session = session_service.get_session(session_id)

        session_service.merge_pool_into_turns(session_id)

    return response_text
