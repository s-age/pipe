from typing import Dict

def delete_session(session_id: str, session_service=None) -> Dict[str, str]:
    """
    Deletes a specified session, including its session file and any backups.
    """
    if not session_service:
        return {"error": "This tool requires a session_service."}

    try:
        session_service.delete_session(session_id)
        return {"message": f"Successfully deleted session {session_id}."}
    except Exception as e:
        return {"error": f"Failed to delete session {session_id}: {e}"}
