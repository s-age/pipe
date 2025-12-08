"""Sessions move to backup action."""

from typing import TypedDict

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_sessions import DeleteSessionsRequest
from pipe.web.service_container import get_session_management_service


class BulkMoveResult(TypedDict):
    """Result of bulk session move operations."""

    message: str
    moved_count: int
    total_requested: int


class SessionsMoveToBackup(BaseAction):
    """
    Action to bulk move multiple sessions to backup.

    Moves selected sessions from index.json and moves session files to backup directory.
    """

    body_model = DeleteSessionsRequest  # Legacy pattern: no path params

    def execute(self) -> BulkMoveResult:
        request_data = DeleteSessionsRequest(**self.request_data.get_json())

        # Move sessions to backup
        moved_count = get_session_management_service().move_sessions_to_backup(
            request_data.session_ids
        )

        return {
            "message": (
                f"Successfully moved {moved_count} out of "
                f"{len(request_data.session_ids)} sessions to backup."
            ),
            "moved_count": moved_count,
            "total_requested": len(request_data.session_ids),
        }
