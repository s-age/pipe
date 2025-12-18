"""Tool for retrieving final turns from multiple sessions.

This tool enables efficient batch retrieval of the last model response
from multiple child sessions, avoiding the need for multiple individual
session queries.
"""

from pipe.core.factories.settings_factory import SettingsFactory
from pipe.core.models.tool_result import ToolResult
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.utils.path import get_project_root


def get_sessions_final_turns(
    session_ids: list[str], project_root: str | None = None
) -> ToolResult:
    """
    Retrieve the final model response turn from multiple sessions.

    Args:
        session_ids: List of session IDs to retrieve final turns from
        project_root: Project root path (auto-detected if not provided)

    Returns:
        ToolResult containing a list of final turns for each session

    Example:
        >>> get_sessions_final_turns(session_ids=["abc123", "def456"])
        {
            "sessions": [
                {
                    "session_id": "abc123",
                    "final_turn": {
                        "type": "model_response",
                        "content": "Task completed successfully",
                        "timestamp": "2025-12-18T12:00:00+09:00"
                    }
                },
                {
                    "session_id": "def456",
                    "final_turn": {
                        "type": "model_response",
                        "content": "Analysis complete",
                        "timestamp": "2025-12-18T12:05:00+09:00"
                    }
                }
            ]
        }

    Note:
        - Only retrieves the final model_response turn from each session
        - Skips sessions that don't exist or have no model_response turns
        - Useful for efficiently collecting results from parallel/serial child agents
    """
    if not session_ids:
        return ToolResult(data={"sessions": []}, error="No session IDs provided")

    if project_root is None:
        project_root = get_project_root()

    # Initialize repository
    settings = SettingsFactory.get_settings(project_root)
    repository = SessionRepository(project_root, settings)

    results: list[dict[str, str | dict[str, str] | None]] = []

    for session_id in session_ids:
        try:
            # Load session
            session = repository.find(session_id)
            if not session:
                results.append(
                    {
                        "session_id": session_id,
                        "final_turn": None,
                        "error": "Session not found",
                    }
                )
                continue

            # Find the last model_response turn
            final_turn: dict[str, str] | None = None
            for turn in reversed(session.turns):
                if turn.type == "model_response":
                    final_turn = {
                        "type": turn.type,
                        "content": turn.content,
                        "timestamp": turn.timestamp,
                    }
                    break

            error_msg: str | None = (
                "No model_response turn found" if final_turn is None else None
            )
            results.append(
                {
                    "session_id": session_id,
                    "final_turn": final_turn,
                    "error": error_msg,
                }
            )

        except Exception as e:
            results.append(
                {
                    "session_id": session_id,
                    "final_turn": None,
                    "error": str(e),
                }
            )

    return ToolResult(data={"sessions": results})
