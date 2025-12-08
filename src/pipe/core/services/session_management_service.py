"""
Session Management Service

Handles bulk operations for session management including deletion, backup, and listing.
"""

from pipe.core.collections.backup_files import BackupFiles, SessionSummary
from pipe.core.collections.files_to_delete import FilesToDelete
from pipe.core.collections.files_to_move import FilesToMove
from pipe.core.repositories.session_repository import SessionRepository


class SessionManagementService:
    """
    Service for managing multiple sessions including bulk operations.

    Responsibilities:
    - Bulk session deletion
    - Moving sessions to backup
    - Listing sessions in backup
    """

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def delete_sessions(self, session_ids: list[str]) -> int:
        """
        Bulk delete multiple sessions.

        Args:
            session_ids: List of session IDs to delete

        Returns:
            Number of successfully deleted sessions
        """
        files_to_delete = FilesToDelete(session_ids, self.repository)
        return files_to_delete.execute()

    def move_sessions_to_backup(self, session_ids: list[str]) -> int:
        """
        Move multiple sessions to backup directory and remove from index.

        Args:
            session_ids: List of session IDs to move to backup

        Returns:
            Number of successfully moved sessions
        """
        files_to_move = FilesToMove(session_ids, self.repository)
        return files_to_move.execute()

    def list_backup_sessions(self) -> list[SessionSummary]:
        """
        List all sessions in the backup directory.

        Returns:
            List of SessionSummary objects containing session metadata
        """
        backup_files = BackupFiles(self.repository)
        return backup_files.list_sessions()

    def delete_backup_sessions(self, session_ids: list[str]) -> int:
        """
        Bulk delete multiple backup sessions.

        Args:
            session_ids: List of session IDs to delete backups for

        Returns:
            Number of successfully deleted backup sessions
        """
        backup_files = BackupFiles(self.repository)
        return backup_files.delete(session_ids)

    def delete_backups_by_session_ids(self, session_ids: list[str]) -> int:
        """
        Delete backup sessions by their session IDs.

        This method handles the conversion from session_ids to file_paths internally.

        Args:
            session_ids: List of session IDs whose backups should be deleted

        Returns:
            Number of successfully deleted backup files
        """
        backup_files = BackupFiles(self.repository)
        backup_sessions = backup_files.list_sessions()

        # Convert session_ids to file_paths
        file_paths = [
            session.file_path
            for session in backup_sessions
            if session.session_id in session_ids
        ]

        return backup_files.delete_files(file_paths)

    def delete_backup_files(self, file_paths: list[str]) -> int:
        """
        Delete specific backup files.

        Args:
            file_paths: List of file paths to delete

        Returns:
            Number of successfully deleted files
        """
        backup_files = BackupFiles(self.repository)
        return backup_files.delete_files(file_paths)
