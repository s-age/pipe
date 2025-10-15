from typing import Dict, Any

def replace_session_turns(session_id: str, start_turn: int, end_turn: int, summary: str, session_manager=None) -> Dict[str, Any]:
    """
    Replaces a specified range of turns in a target session's history with a summary.
    This action is irreversible and automatically creates a backup.
    """
    if not session_manager or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        # Convert 1-based turn numbers to 0-based indices
        start_index = start_turn - 1
        end_index = end_turn - 1
        session_manager.history_manager.replace_turn_range_with_summary(session_id, summary, start_index, end_index)
        return {"message": f"Successfully replaced turns {start_turn}-{end_turn} in session {session_id} with a summary."}
    except Exception as e:
        return {"error": f"Failed to replace turns in session {session_id}: {e}"}
