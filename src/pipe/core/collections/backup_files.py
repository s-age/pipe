"""
Collection for managing session files in the backup directory.

Provides type-safe container for querying backup files.
"""

import json
import os
from typing import Any

from pipe.core.repositories.session_repository import SessionRepository


class BackupFiles:
    """
    Collection representing session files in the backup directory.

    Provides methods to list and query backup files.
    """

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def list_sessions(self) -> list[dict[str, Any]]:
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

                                    # Remove .json extension and hash prefix
                                    name_without_ext = filename.replace(".json", "")
                                    # Split by first '-' to separate hash from datetime
                                    parts = name_without_ext.split("-", 1)
                                    if len(parts) == 2:
                                        datetime_str = parts[
                                            1
                                        ]  # 2025-12-04T075555.140300+0900
                                        # Parse: YYYY-MM-DDTHHMMSS.ffffffTZTZ
                                        date_part, rest = datetime_str.split("T", 1)
                                        # 2025-12-04, 075555.140300+0900
                                        time_microsec_tz = rest
                                        # Extract time, microseconds, and timezone
                                        # Format: 075555.140300+0900
                                        # -> 07:55:55.140300+09:00
                                        time_str = time_microsec_tz[:6]  # 075555
                                        formatted_time = ":".join(
                                            [
                                                time_str[0:2],
                                                time_str[2:4],
                                                time_str[4:6],
                                            ]
                                        )
                                        # Get microseconds and timezone
                                        remaining = time_microsec_tz[6:]  # .140300+0900
                                        # Split by + or -
                                        if "+" in remaining:
                                            microsec_part, tz_part = remaining.split(
                                                "+"
                                            )
                                            tz_sign = "+"
                                        else:
                                            microsec_part, tz_part = remaining.split(
                                                "-"
                                            )
                                            tz_sign = "-"
                                        microsec_str = microsec_part.lstrip(
                                            "."
                                        )  # 140300
                                        formatted_tz = (
                                            f"{tz_sign}{tz_part[0:2]}:{tz_part[2:]}"
                                        )
                                        iso_str = (
                                            f"{date_part}T{formatted_time}."
                                            f"{microsec_str}{formatted_tz}"
                                        )
                                        dt = datetime.fromisoformat(iso_str)
                                        deleted_at = dt.isoformat()
                                    else:
                                        deleted_at = None
                                except (ValueError, IndexError):
                                    deleted_at = None

                                sessions.append(
                                    {
                                        "session_id": session_id,
                                        "file_path": path,
                                        "purpose": purpose,
                                        "deleted_at": deleted_at,
                                        "session_data": data,
                                    }
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
