from pipe.core.models.todo import TodoItem


def edit_todos(
    todos: list[TodoItem], session_service=None, session_id=None
) -> dict[str, str]:
    """
    Edits the list of TODO items directly within the session data.

    Example:
    edit_todos(todos=[{"title": "test1", "description": "", "checked": False},
    {"title": "test2", "description": "", "checked": False}])
    """
    if not session_service or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        session = session_service.get_session(session_id)
        if not session:
            return {"error": f"Session with ID {session_id} not found."}
        from pipe.core.domains.todos import update_todos_in_session

        update_todos_in_session(session, todos)
        session_service.repository.save(session)
        return {"message": f"Todos successfully updated in session {session_id}."}
    except Exception as e:
        return {"error": f"Failed to update todos in session: {e}"}
