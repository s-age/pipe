from typing import List, Dict, Any

def edit_todos(
    todos: List[Dict[str, Any]],
    session_manager=None,
    session_id=None
) -> Dict[str, Any]:
    """
    Edits the list of TODO items directly within the session data.
    """
    if not session_manager or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        # Access the history_manager through the session_manager
        session_manager.history_manager.update_todos(session_id, todos)
        return {"message": f"Todos successfully updated in session {session_id}."}
    except Exception as e:
        return {"error": f"Failed to update todos in session: {e}"}