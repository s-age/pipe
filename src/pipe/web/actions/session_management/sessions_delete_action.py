"""Sessions delete action."""

from typing import TypedDict

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_sessions import DeleteSessionsRequest
from pipe.web.service_container import get_session_management_service


class BulkOperationResult(TypedDict):
    """Result of bulk session operations."""

    message: str
    deleted_count: int
    total_requested: int


class SessionsDeleteAction(BaseAction):
    """
    Action to bulk delete multiple sessions.

    Deletes multiple sessions and returns the count of successfully deleted sessions.
    """

    body_model = DeleteSessionsRequest  # Legacy pattern: no path params

    def execute(self) -> BulkOperationResult:
        request_data = DeleteSessionsRequest(**self.request_data.get_json())

        # Delete sessions via service
        deleted_count = get_session_management_service().delete_sessions(
            request_data.session_ids
        )

        return {
            "message": (
                f"Successfully deleted {deleted_count} out of "
                f"{len(request_data.session_ids)} sessions."
            ),
            "deleted_count": deleted_count,
            "total_requested": len(request_data.session_ids),
        }
