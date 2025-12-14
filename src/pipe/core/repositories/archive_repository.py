"""
Repository for managing backup and archive sessions.

Handles the persistence of archived sessions in the backups directory,
separate from active sessions.
"""

import os

from pipe.core.models.session import Session
from pipe.core.repositories.file_repository import FileRepository


class ArchiveRepository(FileRepository):
    """
    Manages backup and archived sessions in the backups directory.

    Unlike SessionRepository which handles active sessions,
    ArchiveRepository manages timestamped backups of sessions
    that have been archived or backed up.
    """

    def __init__(self, backups_dir: str):
        """
        Initialize the ArchiveRepository.

        Args:
            backups_dir: Path to the backups directory (typically sessions/backups/)
        """
        super().__init__()
        self.backups_dir = backups_dir

        # Ensure backups directory exists
        os.makedirs(self.backups_dir, exist_ok=True)

    def save_backup(self, session_id: str, session: Session, timestamp: str) -> str:
        """
        Save a backup of a session with a timestamp.

        Args:
            session_id: The session ID
            session: The Session object to backup
            timestamp: ISO format timestamp string

        Returns:
            The path where the backup was saved
        """
        # Create backup filename: {session_id}_{timestamp}.json
        # Replace slashes in session_id with underscores for filesystem compatibility
        safe_session_id = session_id.replace("/", "__")
        backup_filename = f"{safe_session_id}_{timestamp}.json"
        backup_path = os.path.join(self.backups_dir, backup_filename)

        # Serialize and write the backup
        session_data = session.model_dump(mode="json")
        self._write_json(backup_path, session_data)

        return backup_path

    def list_backups(self, session_id: str) -> list[tuple[str, str]]:
        """
        List all backups for a given session.

        Args:
            session_id: The session ID to find backups for

        Returns:
            List of (backup_filename, backup_path) tuples,
            sorted by timestamp (most recent first)
        """
        safe_session_id = session_id.replace("/", "__")
        prefix = f"{safe_session_id}_"

        backups = []
        for filename in os.listdir(self.backups_dir):
            if filename.startswith(prefix) and filename.endswith(".json"):
                backup_path = os.path.join(self.backups_dir, filename)
                backups.append((filename, backup_path))

        # Sort by timestamp (descending - most recent first)
        backups.sort(key=lambda x: x[0], reverse=True)
        return backups

    def restore_backup(self, backup_path: str) -> Session:
        """
        Restore a session from a backup file.

        Args:
            backup_path: Path to the backup file

        Returns:
            The restored Session object

        Raises:
            FileNotFoundError: If the backup file doesn't exist
            ValueError: If the backup file is invalid JSON or invalid Session data
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        data = self._read_json(backup_path)
        return Session.model_validate(data)

    def delete_backup(self, backup_path: str) -> bool:
        """
        Delete a backup file.

        Args:
            backup_path: Path to the backup file

        Returns:
            True if the backup was deleted, False if it didn't exist
        """
        if os.path.exists(backup_path):
            os.remove(backup_path)
            return True
        return False

    def delete_all_backups(self, session_id: str) -> int:
        """
        Delete all backups for a given session.

        Args:
            session_id: The session ID to delete backups for

        Returns:
            The number of backups deleted
        """
        backups = self.list_backups(session_id)
        deleted_count = 0

        for _, backup_path in backups:
            if self.delete_backup(backup_path):
                deleted_count += 1

        return deleted_count
