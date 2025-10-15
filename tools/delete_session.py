from typing import Dict, Any

def delete_session(session_id: str, session_manager=None) -> Dict[str, Any]:
    """
    Deletes a specified session, including its session file and any backups.
    """
    if not session_manager:
        return {"error": "This tool requires a session_manager."}

    try:
        session_manager.history_manager.delete_session(session_id)
        return {"message": f"Successfully deleted session {session_id}."}
    except Exception as e:
        return {"error": f"Failed to delete session {session_id}: {e}"}
