"""Sessions delete backup action."""

from typing import TypedDict

from flask import Request
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_sessions import DeleteBackupRequest
from pipe.web.service_container import get_session_management_service


class BulkOperationResult(TypedDict):
    """Result of bulk session operations."""

    message: str
    deleted_count: int
    total_requested: int


class SessionsDeleteBackupAction(BaseAction):
    """
    Action to bulk delete multiple backup sessions.

    Deletes multiple backup sessions and returns the count of successfully
    deleted sessions.
    """

    request_model = DeleteBackupRequest

    def __init__(
        self,
        validated_request: DeleteBackupRequest | None = None,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,
    ):
        super().__init__(params, request_data, **kwargs)
        self.validated_request = validated_request

    def execute(self) -> BulkOperationResult:
        if not self.validated_request:
            raise ValueError("Request is required")

        request_data = self.validated_request
        service = get_session_management_service()

        # Determine whether to use session_ids or file_paths
        if request_data.session_ids:
            deleted_count = service.delete_backups_by_session_ids(
                request_data.session_ids
            )
            total_requested = len(request_data.session_ids)
        else:
            deleted_count = service.delete_backup_files(request_data.file_paths or [])
            total_requested = len(request_data.file_paths or [])

        return {
            "message": (
                f"Successfully deleted {deleted_count} out of "
                f"{total_requested} backup items."
            ),
            "deleted_count": deleted_count,
            "total_requested": total_requested,
        }
