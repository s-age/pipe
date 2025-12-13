import json
import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory


def get_session(
    session_id: str | None = None,
    session_service=None,
) -> str:
    """
    Retrieves the session data for the given session_id and returns the turns as text.

    Returns:
        JSON string containing session information
    """
    if not session_id:
        return json.dumps({"error": "session_id is required."})

    if not session_service:
        project_root = os.getcwd()
        try:
            settings = SettingsFactory.get_settings(project_root)
        except Exception as e:
            return json.dumps({"error": f"Failed to load settings: {e}"})

        factory = ServiceFactory(project_root, settings)
        session_service = factory.create_session_service()

    session = session_service.get_session(session_id)
    if not session:
        return json.dumps({"error": f"Session {session_id} not found."})

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

    result = {
        "session_id": session_id,
        "turns": turns_text,
        "turns_count": len(session.turns),
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
