from typing import Dict, Any

def delete_todos(session_manager=None, session_id=None) -> Dict[str, Any]:
    """
    Deletes the list of TODO items from the current session data.
    """
    if not session_manager or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        session_manager.history_manager.delete_todos(session_id)
        return {"message": f"Todos successfully deleted from session {session_id}."}
    except Exception as e:
        return {"error": f"Failed to delete todos from session: {e}"}
