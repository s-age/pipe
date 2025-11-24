from typing import Any


def get_session(
    session_id: str,
    session_service=None,
) -> dict[str, Any]:
    """
    Retrieves the session data for the given session_id and returns the turns as text.
    """
    if not session_service:
        return {"error": "This tool requires a session_service."}

    session = session_service.get_session(session_id)
    if not session:
        return {"error": f"Session {session_id} not found."}

    # Convert turns to text
    turns_text = []
    for turn in session.turns:
        if turn.type == "user_task":
            turns_text.append(f"User: {turn.instruction}")
        elif turn.type == "model_response":
            turns_text.append(f"Assistant: {turn.content}")
        else:
            turns_text.append(
                f"{turn.type}: "
                f"{getattr(turn, 'content', getattr(turn, 'instruction', str(turn)))}"
            )

    return {
        "session_id": session_id,
        "turns": turns_text,
        "turns_count": len(session.turns),
    }
