"""
Repository for managing backup and archive sessions.

Handles the persistence of archived sessions in the backups directory,
separate from active sessions.
"""

import hashlib
import json
import os
import zoneinfo
from datetime import datetime

from pipe.core.models.session import Session
from pipe.core.repositories.file_repository import FileRepository, file_lock
from pipe.core.utils.datetime import get_current_timestamp


class SessionSummary:
    """Summary information for a backup session."""

    def __init__(
        self,
        session_id: str,
        file_path: str,
        purpose: str | None,
        deleted_at: str | None,
    ):
        self.session_id = session_id
        self.file_path = file_path
        self.purpose = purpose
        self.deleted_at = deleted_at


class ArchiveRepository(FileRepository):
    """
    Manages backup and archived sessions in the backups directory.

    Unlike SessionRepository which handles active sessions,
    ArchiveRepository manages timestamped backups of sessions
    that have been archived or backed up.

    Note:
        - Backup file name format: {sha256(session_id)}-{timestamp}.json
        - Multiple backup generations per session are not supported (only latest kept)
    """

    def __init__(self, backups_dir: str, timezone_obj: zoneinfo.ZoneInfo | None = None):
        """
        Initialize the ArchiveRepository.

        Args:
            backups_dir: Path to the backups directory (typically sessions/backups/)
            timezone_obj: Timezone object for timestamp formatting (defaults to UTC)
        """
        super().__init__()
        self.backups_dir = backups_dir
        self.timezone_obj = timezone_obj or zoneinfo.ZoneInfo("UTC")

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
        # Create backup filename: {hash(session_id)}-{timestamp}.json
        session_hash = hashlib.sha256(session_id.encode("utf-8")).hexdigest()

        # Ensure timestamp is filesystem safe (remove colons)
        safe_timestamp = timestamp.replace(":", "")

        backup_filename = f"{session_hash}-{safe_timestamp}.json"
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
        session_hash = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
        prefix = f"{session_hash}-"

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
        if data is None:
            # If _read_json returns None, it means JSON was invalid or file was empty.
            # We raise a ValueError to indicate invalid data format.
            raise ValueError(f"Invalid JSON data in backup file: {backup_path}")
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

    def list(self) -> list[SessionSummary]:
        """
        List all backed up sessions.

        Returns:
            List of SessionSummary objects sorted by deleted_at (most recent first)
        """
        summaries = []

        for filename in os.listdir(self.backups_dir):
            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(self.backups_dir, filename)

            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                session_id = data.get("session_id")
                if not session_id:
                    continue

                purpose = data.get("purpose")

                # Extract deleted_at from filename
                # Format: {hash}-YYYY-MM-DDTHHMMSS.ffffff+ZZZZ.json
                deleted_at = self._extract_deleted_at(filename)

                summaries.append(
                    SessionSummary(
                        session_id=session_id,
                        file_path=file_path,
                        purpose=purpose,
                        deleted_at=deleted_at,
                    )
                )
            except Exception:
                # Skip corrupted files
                continue

        # Sort by deleted_at descending
        summaries.sort(key=lambda s: s.deleted_at or "", reverse=True)

        return summaries

    def save(self, session: Session) -> str:
        """
        Save a session as a backup.

        Args:
            session: The session to backup

        Returns:
            Path to the saved backup file
        """
        session_hash = hashlib.sha256(session.session_id.encode("utf-8")).hexdigest()

        timestamp = get_current_timestamp(self.timezone_obj).replace(":", "")
        backup_filename = f"{session_hash}-{timestamp}.json"
        backup_path = os.path.join(self.backups_dir, backup_filename)

        lock_path = f"{backup_path}.lock"

        with file_lock(lock_path):
            self._write_json(backup_path, session.model_dump(mode="json"))

        return backup_path

    def restore(self, session_id: str) -> Session | None:
        """
        Restore the latest backup for a given session ID.

        Args:
            session_id: The session ID to restore

        Returns:
            Restored Session instance, or None if no backup exists
        """
        session_hash = hashlib.sha256(session_id.encode("utf-8")).hexdigest()

        # Find all matching backup files
        matching_files = [
            f
            for f in os.listdir(self.backups_dir)
            if f.startswith(session_hash) and f.endswith(".json")
        ]

        if not matching_files:
            return None

        # Select the latest backup (sort by filename)
        latest = sorted(matching_files)[-1]
        backup_path = os.path.join(self.backups_dir, latest)

        lock_path = f"{backup_path}.lock"

        with file_lock(lock_path):
            data = self._read_json(backup_path)

        if data is None:
            return None

        return Session.model_validate(data)

    def delete(self, session_id: str) -> bool:
        """
        Delete all backups for a given session ID.

        Returns:
            True if at least one backup was deleted
        """
        session_hash = hashlib.sha256(session_id.encode("utf-8")).hexdigest()

        deleted = False

        for filename in os.listdir(self.backups_dir):
            if filename.startswith(session_hash) and filename.endswith(".json"):
                backup_path = os.path.join(self.backups_dir, filename)
                lock_path = f"{backup_path}.lock"

                try:
                    with file_lock(lock_path):
                        if os.path.exists(backup_path):
                            os.remove(backup_path)
                            deleted = True
                except OSError:
                    continue

        return deleted

    def _extract_deleted_at(self, filename: str) -> str | None:
        """
        Extract deleted_at timestamp from filename and convert to ISO 8601 format.

        Example:
            hash-2025-12-14T103045.123456+0900.json
            -> "2025-12-14T10:30:45.123456+09:00"

        Args:
            filename: The backup filename

        Returns:
            ISO 8601 formatted timestamp, or None if parsing fails
        """
        import re

        match = re.search(r"(\d{4}-\d{2}-\d{2}T\d{6}\.\d{6}[+-]\d{4})", filename)
        if not match:
            return None

        datetime_str = match.group(1)
        try:
            # Parse the datetime string using strptime and convert to ISO format
            dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H%M%S.%f%z")
            return dt.isoformat()
        except (ValueError, IndexError):
            return None
