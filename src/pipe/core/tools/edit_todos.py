from typing import List, Dict
from pipe.core.models.todo import TodoItem

def edit_todos(
    todos: List[TodoItem],
    session_service=None,
    session_id=None
) -> Dict[str, str]:
    """
    Edits the list of TODO items directly within the session data.

    Example:
    edit_todos(todos=[{"title": "test1", "description": "", "checked": False}, {"title": "test2", "description": "", "checked": False}])
    """
    if not session_service or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        # Access the history_manager through the session_service
        session_service.update_todos(session_id, todos)
        return {"message": f"Todos successfully updated in session {session_id}."}
    except Exception as e:
        return {"error": f"Failed to update todos in session: {e}"}