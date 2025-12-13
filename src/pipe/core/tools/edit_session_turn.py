import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory


def edit_session_turn(
    turn: int,
    new_content: str,
    session_service=None,
    session_id: str | None = None,
) -> dict[str, str]:
    """
    Edits the content of a specified turn in a target session's history.
    This action is irreversible and automatically creates a backup.

    Args:
        session_id: The ID of the session. If None, it attempts to read from
            PIPE_SESSION_ID.
        turn: The 1-based turn number to edit.
        new_content: The new content to replace the old content with.
        session_service: (Legacy) Ignored in favor of ServiceFactory.
    """
    # Resolve session_id from argument or environment variable
    target_session_id = session_id or os.environ.get("PIPE_SESSION_ID")

    if not target_session_id:
        return {
            "error": (
                "This tool requires a session_id (provided via argument or "
                "PIPE_SESSION_ID)."
            )
        }

    if turn < 1:
        return {"error": "Turn number must be 1 or greater."}

    try:
        project_root = os.getcwd()

        # Load settings
        settings = SettingsFactory.get_settings(project_root)

        factory = ServiceFactory(project_root, settings)
        turn_service = factory.create_session_turn_service()
        # Access repository through service (needed for backup and find)
        # Assuming SessionTurnService has a public repository attribute as seen in code
        repository = turn_service.repository

        # Convert 1-based turn number to 0-based index
        index = turn - 1

        session = repository.find(target_session_id)
        if not session or index >= len(session.turns):
            return {"error": f"Turn {turn} not found in session {target_session_id}"}

        # Validate turn type and prepare update data
        target_turn = session.turns[index]
        if target_turn.type == "user_task":
            update_data = {"instruction": new_content}
        elif target_turn.type == "model_response":
            update_data = {"content": new_content}
        else:
            return {"error": f"Cannot edit turn of type {target_turn.type}"}

        # Create backup before editing
        repository.backup(session)

        # Perform the edit
        turn_service.edit_turn(target_session_id, index, update_data)

        return {
            "message": (
                f"Successfully edited turn {turn} in session {target_session_id}."
            )
        }
    except Exception as e:
        return {"error": f"Failed to edit turn in session {target_session_id}: {e}"}
