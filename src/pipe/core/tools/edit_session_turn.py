def edit_session_turn(
    session_id: str, turn: int, new_content: str, session_service=None
) -> dict[str, str]:
    """
    Edits the content of a specified turn in a target session's history.
    This action is irreversible and automatically creates a backup.
    """
    if not session_service or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        # Convert 1-based turn number to 0-based index
        index = turn - 1
        session = session_service.history_manager.get_session(session_id)
        if not session or index >= len(session.turns):
            return {"error": f"Turn {turn} not found in session {session_id}"}

        target_turn = session.turns[index]
        if target_turn.type == "user_task":
            update_data = {"instruction": new_content}
        elif target_turn.type == "model_response":
            update_data = {"content": new_content}
        else:
            return {"error": f"Cannot edit turn of type {target_turn.type}"}

        session_service.history_manager.edit_turn(session_id, index, update_data)
        return {
            "message": (f"Successfully edited turn {turn} in session {session_id}.")
        }
    except Exception as e:
        return {"error": f"Failed to edit turn in session {session_id}: {e}"}
