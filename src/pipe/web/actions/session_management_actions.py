from typing import TypedDict

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_sessions import (
    DeleteBackupRequest,
    DeleteSessionsRequest,
)


class BulkOperationResult(TypedDict):
    """Result of bulk session operations."""

    message: str
    deleted_count: int
    total_requested: int


class BulkMoveResult(TypedDict):
    """Result of bulk session move operations."""

    message: str
    moved_count: int
    total_requested: int


class SessionsDeleteAction(BaseAction):
    """
    Action to bulk delete multiple sessions.

    Deletes multiple sessions and returns the count of successfully deleted sessions.
    """

    body_model = DeleteBackupRequest  # Legacy pattern: no path params

    def execute(self) -> BulkOperationResult:
        from pipe.web.service_container import get_session_management_service

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


class SessionsMoveToBackup(BaseAction):
    """
    Action to bulk move multiple sessions to backup.

    Moves selected sessions from index.json and moves session files to backup directory.
    """

    body_model = DeleteSessionsRequest  # Legacy pattern: no path params

    def execute(self) -> BulkMoveResult:
        from pipe.web.service_container import get_session_management_service

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


class SessionsListBackupAction(BaseAction):
    """
    Action to list sessions in the backup directory.

    Returns a list of sessions found in the backup directory with their
    session IDs and file paths.
    """

    def execute(self) -> dict[str, list[dict]]:
        from pipe.web.service_container import get_session_management_service

        sessions = get_session_management_service().list_backup_sessions()
        # Convert SessionSummary objects to dicts for JSON serialization
        return {"sessions": [session.model_dump() for session in sessions]}


class SessionsDeleteBackupAction(BaseAction):
    """
    Action to bulk delete multiple backup sessions.

    Deletes multiple backup sessions and returns the count of successfully
    deleted sessions.
    """

    body_model = DeleteBackupRequest  # Legacy pattern: no path params

    def execute(self) -> BulkOperationResult:
        from pipe.web.service_container import get_session_management_service

        request_data = DeleteBackupRequest(**self.request_data.get_json())

        # Determine whether to use session_ids or file_paths
        if request_data.session_ids:
            # Convert session_ids to file_paths
            file_paths = []
            service = get_session_management_service()
            backup_sessions = service.list_backup_sessions()
            for session in backup_sessions:
                if session.session_id in request_data.session_ids:
                    file_paths.append(session.file_path)
            deleted_count = service.delete_backup_files(file_paths)
            total_requested = len(request_data.session_ids)
        else:
            # Use file_paths directly
            deleted_count = get_session_management_service().delete_backup_files(
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
