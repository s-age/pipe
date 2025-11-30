def delete_session_turns(
    session_id: str, turns: list[int], session_service=None
) -> dict[str, str]:
    """
    Deletes specified turns from a target session's history.
    This action is irreversible and automatically creates a backup.
    """
    if not session_service or not session_id:
        return {"error": "This tool requires an active session."}

    try:
        # Convert 1-based turn numbers to 0-based indices
        indices = [turn - 1 for turn in turns]
        session_service.history_manager.delete_turns(session_id, indices)
        return {
            "message": (
                f"Successfully deleted turns {turns} from session {session_id}."
            )
        }
    except Exception as e:
        return {"error": f"Failed to delete turns from session {session_id}: {e}"}
