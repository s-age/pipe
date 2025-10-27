def delete_todos(session_service=None, session_id=None) -> dict[str, str]:
    """
    Deletes the list of TODO items from the current session data.
    """
    if not session_service or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        session_service.delete_todos(session_id)
        return {"message": f"Todos successfully deleted from session {session_id}."}
    except Exception as e:
        return {"error": f"Failed to delete todos from session: {e}"}
