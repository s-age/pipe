"""Sessions delete action."""

from typing import TypedDict

from pipe.core.services.session_management_service import SessionManagementService
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_sessions import DeleteSessionsRequest


class BulkOperationResult(TypedDict):
    """Result of bulk session operations."""

    message: str
    deleted_count: int
    total_requested: int


class SessionsDeleteAction(BaseAction):
    """Bulk delete multiple sessions.

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

    def execute(self) -> BulkOperationResult:
        if not self.validated_request:
            raise ValueError("Request is required")

        request_data = self.validated_request

        # Delete sessions via service
        deleted_count = self.session_management_service.delete_sessions(
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
