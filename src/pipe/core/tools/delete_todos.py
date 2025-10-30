def delete_todos(session_service=None, session_id=None) -> dict[str, str]:
    """
    Deletes the list of TODO items from the current session data.
    """
    if not session_service or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        session = session_service.get_session(session_id)
        if not session:
            return {"error": f"Session with ID {session_id} not found."}
        from pipe.core.domains.todos import delete_todos_in_session

        delete_todos_in_session(session)
        session_service._save_session(session)
        return {"message": f"Todos successfully deleted from session {session_id}."}
    except Exception as e:
        return {"error": f"Failed to delete todos from session: {e}"}
