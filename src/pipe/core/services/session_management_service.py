"""
Session Management Service

Handles bulk operations for session management including deletion, backup, and listing.
"""

from typing import Any

from pipe.core.collections.backup_files import BackupFiles
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

    def list_backup_sessions(self) -> list[dict[str, Any]]:
        """
        List all sessions in the backup directory.

        Returns:
            List of dictionaries containing session_id and file_path for each
            backup session
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
