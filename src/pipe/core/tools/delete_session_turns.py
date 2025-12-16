import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory
from pipe.core.models.results.delete_session_turns_result import (
    DeleteSessionTurnsResult,
)
from pipe.core.models.tool_result import ToolResult


def delete_session_turns(
    session_id: str, turns: list[int], session_service=None
) -> ToolResult[DeleteSessionTurnsResult]:
    """
    Deletes specified turns from a target session's history.
    This action is irreversible and automatically creates a backup.

    Args:
        session_id: The ID of the session.
        turns: List of turn numbers (1-based) to delete.
        session_service: (Legacy) Ignored in favor of ServiceFactory.
    """
    try:
        project_root = os.getcwd()

        # Load settings
        settings = SettingsFactory.get_settings(project_root)

        factory = ServiceFactory(project_root, settings)
        turn_service = factory.create_session_turn_service()

        # Convert 1-based turn numbers to 0-based indices
        indices = [turn - 1 for turn in turns]

        turn_service.delete_turns(session_id, indices)

        result = DeleteSessionTurnsResult(
            message=f"Successfully deleted turns {turns} from session {session_id}."
        )
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(
            error=f"Failed to delete turns from session {session_id}: {e}"
        )
