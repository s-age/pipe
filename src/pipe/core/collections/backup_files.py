"""
Collection for managing session files in the backup directory.

Provides type-safe container for querying backup files.
"""

import json
import os
from typing import Any

from pipe.core.repositories.session_repository import SessionRepository
from pydantic import BaseModel


class SessionSummary(BaseModel):
    session_id: str
    file_path: str
    purpose: str | None
    deleted_at: str | None
    session_data: dict[str, Any]  # Raw JSON data from backup file


class BackupFiles:
    """
    Collection representing session files in the backup directory.

    Provides methods to list and query backup files.
    """

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def list_sessions(self) -> list[SessionSummary]:
        """
        List all sessions in the backup directory.

        Returns:
            List of dictionaries containing session_id and file_path for each
            backup session
        """
        backups_dir = self.repository.backups_dir
        sessions = []

        if os.path.exists(backups_dir):
            for filename in os.listdir(backups_dir):
                if filename.endswith(".json"):
                    path = os.path.join(backups_dir, filename)
                    try:
                        with open(path, encoding="utf-8") as f:
                            data = json.load(f)
                            session_id = data.get("session_id")
                            purpose = data.get("purpose")
                            if session_id:
                                # Extract deleted_at from filename
                                # Format: {hash}-{datetime}.json
                                # Example: hash-2025-12-04T075555.140300+0900.json
                                try:
                                    from datetime import datetime

                                    name_without_ext = filename.replace(".json", "")
                                    # Split by first '-' to separate hash from datetime
                                    parts = name_without_ext.split("-", 1)
                                    if len(parts) == 2:
                                        datetime_str = parts[
                                            1
                                        ]  # 2025-12-04T075555.140300+0900
                                        # Parse using strptime with format:
                                        # %Y-%m-%d: date, T: literal, %H%M%S: time,
                                        # %f: microseconds, %z: timezone
                                        dt = datetime.strptime(
                                            datetime_str, "%Y-%m-%dT%H%M%S.%f%z"
                                        )
                                        deleted_at = dt.isoformat()
                                    else:
                                        deleted_at = None
                                except ValueError:
                                    deleted_at = None

                                sessions.append(
                                    SessionSummary(
                                        session_id=session_id,
                                        file_path=path,
                                        purpose=purpose,
                                        deleted_at=deleted_at,
                                        session_data=data,
                                    )
                                )
                    except Exception:
                        # Skip files that can't be read or parsed
                        continue

        return sessions

    def delete(self, session_ids: list[str]) -> int:
        """
        Delete backup files for the given session IDs.

        Args:
            session_ids: List of session IDs to delete backups for

        Returns:
            Number of successfully deleted backup files
        """
        deleted_count = 0
        for session_id in session_ids:
            try:
                self.repository.delete_backup(session_id)
                deleted_count += 1
            except Exception:
                # Continue with other deletions even if one fails
                continue
        return deleted_count

    def delete_files(self, file_paths: list[str]) -> int:
        """
        Delete specific backup files by their paths.

        Args:
            file_paths: List of file paths to delete

        Returns:
            Number of successfully deleted files
        """
        deleted_count = 0
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            except Exception:
                # Continue with other deletions even if one fails
                continue
        return deleted_count
