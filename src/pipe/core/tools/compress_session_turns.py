import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory
from pipe.core.models.results.compress_session_turns_result import (
    CompressSessionTurnsResult,
)
from pipe.core.models.tool_result import ToolResult


def compress_session_turns(
    session_id: str,
    start_turn: int,
    end_turn: int,
    summary: str,
    session_service=None,
) -> ToolResult[CompressSessionTurnsResult]:
    """
    Compresses a specified range of turns in a target session's history with a summary.
    This action is irreversible and automatically creates a backup.
    """
    # Input Validation
    if not session_id:
        return ToolResult(error="session_id is required.")
    if not (isinstance(start_turn, int) and start_turn > 0):
        return ToolResult(error="start_turn must be a positive integer.")
    if not (isinstance(end_turn, int) and end_turn > 0):
        return ToolResult(error="end_turn must be a positive integer.")
    if start_turn > end_turn:
        return ToolResult(error="start_turn cannot be greater than end_turn.")
    if not summary:
        return ToolResult(error="Summary cannot be empty.")

    try:
        # Initialize ServiceFactory and get SessionOptimizationService
        project_root = os.getcwd()

        # Load settings
        settings = SettingsFactory.get_settings(project_root)

        service_factory = ServiceFactory(project_root, settings)
        optimization_service = service_factory.create_session_optimization_service()

        # Convert 1-based turn numbers to 0-based indices
        start_index = start_turn - 1
        end_index = end_turn - 1

        optimization_service.replace_turn_range_with_summary(
            session_id, summary, start_index, end_index
        )

        # Reload session to get updated turn count
        session_service = service_factory.create_session_service()
        updated_session = session_service.get_session(session_id)
        current_turn_count = len(updated_session.turns) if updated_session else 0

        result = CompressSessionTurnsResult(
            message=(
                f"Successfully compressed turns {start_turn}-{end_turn} in session "
                f"{session_id} with a summary. "
                f"Session now has {current_turn_count} turns."
            ),
            current_turn_count=current_turn_count,
        )
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(
            error=f"Failed to compress turns in session {session_id}: {e}"
        )
