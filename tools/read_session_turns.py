from typing import Dict, Any, List

def read_session_turns(session_id: str, start_turn: int, end_turn: int, session_manager=None) -> Dict[str, Any]:
    """
    Reads a specified range of turns from a target session's history.
    """
    if not session_manager or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        # Note: The tool is being called from within a session, but it's targeting another session.
        # The `session_manager` is the key to accessing all sessions.
        turns = session_manager.history_manager.get_session_turns_range(session_id, start_turn, end_turn)
        return {"turns": turns}
    except Exception as e:
        return {"error": f"Failed to read turns from session {session_id}: {e}"}
