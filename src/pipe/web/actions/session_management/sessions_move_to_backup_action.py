"""Sessions move to backup action."""

from typing import TypedDict

from pipe.core.services.session_management_service import SessionManagementService
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_sessions import DeleteSessionsRequest


class BulkMoveResult(TypedDict):
    """Result of bulk session move operations."""

    message: str
    moved_count: int
    total_requested: int


class SessionsMoveToBackup(BaseAction):
    """Bulk move multiple sessions to backup.

    This action uses constructor injection for SessionManagementService,
    following the DI pattern.
    """

    request_model = DeleteSessionsRequest

    def __init__(
        self,
        session_management_service: SessionManagementService,
        validated_request: DeleteSessionsRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.session_management_service = session_management_service
        self.validated_request = validated_request

    def execute(self) -> BulkMoveResult:
        if not self.validated_request:
            raise ValueError("Request is required")

        request_data = self.validated_request

        # Move sessions to backup
        moved_count = self.session_management_service.move_sessions_to_backup(
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
