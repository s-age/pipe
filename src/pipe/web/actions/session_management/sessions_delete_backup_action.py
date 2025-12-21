"""Sessions delete backup action."""

from typing import TypedDict

from pipe.core.services.session_management_service import SessionManagementService
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_sessions import DeleteBackupRequest


class BulkOperationResult(TypedDict):
    """Result of bulk session operations."""

    message: str
    deleted_count: int
    total_requested: int


class SessionsDeleteBackupAction(BaseAction):
    """Bulk delete multiple backup sessions.

    This action uses constructor injection for SessionManagementService,
    following the DI pattern.
    """

    request_model = DeleteBackupRequest

    def __init__(
        self,
        session_management_service: SessionManagementService,
        validated_request: DeleteBackupRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.session_management_service = session_management_service
        self.validated_request = validated_request

    def execute(self) -> BulkOperationResult:
        if not self.validated_request:
            raise ValueError("Request is required")

        request_data = self.validated_request

        # Determine whether to use session_ids or file_paths
        if request_data.session_ids:
            service = self.session_management_service
            deleted_count = service.delete_backups_by_session_ids(
                request_data.session_ids
            )
            total_requested = len(request_data.session_ids)
        else:
            deleted_count = self.session_management_service.delete_backup_files(
                request_data.file_paths or []
            )
            total_requested = len(request_data.file_paths or [])

        return {
            "message": (
                f"Successfully deleted {deleted_count} out of "
                f"{total_requested} backup items."
            ),
            "deleted_count": deleted_count,
            "total_requested": total_requested,
        }
