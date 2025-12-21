"""Repository for managing process PID files."""

import os
from pathlib import Path

from pipe.core.repositories.file_repository import FileRepository


class ProcessFileRepository(FileRepository):
    """
    Handles persistence of process PID files.

    Responsibilities:
    - Read/write PID from/to .pid files
    - Check if PID file exists
    - Delete PID files
    - Sanitize session IDs for filesystem safety

    File format: Simple text file containing only the PID number
    File naming: {session_id}.pid
    """

    def __init__(self, processes_dir: str):
        """
        Initialize the process file repository.

        Args:
            processes_dir: Directory where .pid files are stored
        """
        super().__init__()
        self.processes_dir = processes_dir
        Path(self.processes_dir).mkdir(parents=True, exist_ok=True)

    def _sanitize_session_id(self, session_id: str) -> str:
        """
        Sanitize session_id to be filesystem-safe.

        Args:
            session_id: Original session identifier (may contain / for subagents)

        Returns:
            Filesystem-safe session identifier
        """
        return session_id.replace("/", "_").replace("\\", "_")

    def _get_pid_file_path(self, session_id: str) -> str:
        """
        Get the path to the PID file for a session.

        Args:
            session_id: Session identifier

        Returns:
            Path to the PID file
        """
        safe_session_id = self._sanitize_session_id(session_id)
        return os.path.join(self.processes_dir, f"{safe_session_id}.pid")

    def read_pid(self, session_id: str) -> int | None:
        """
        Read the PID from a session's PID file.

        Args:
            session_id: Session identifier

        Returns:
            PID if file exists and is valid, None otherwise
        """
        pid_file_path = self._get_pid_file_path(session_id)
        if not os.path.exists(pid_file_path):
            return None

        try:
            with open(pid_file_path, encoding="utf-8") as f:
                content = f.read().strip()
                return int(content)
        except (OSError, ValueError):
            # File doesn't exist, can't be read, or contains invalid PID
            return None

    def write_pid(self, session_id: str, pid: int) -> None:
        """
        Write a PID to a session's PID file atomically.

        Args:
            session_id: Session identifier
            pid: Process ID to write

        Note:
            Uses temp file + rename for atomic writes
        """
        pid_file_path = self._get_pid_file_path(session_id)
        temp_path = f"{pid_file_path}.tmp"

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(str(pid))
            os.rename(temp_path, pid_file_path)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def delete_pid_file(self, session_id: str) -> None:
        """
        Delete the PID file for a session.

        Args:
            session_id: Session identifier

        Note:
            Safe to call even if file doesn't exist
        """
        pid_file_path = self._get_pid_file_path(session_id)
        if os.path.exists(pid_file_path):
            try:
                os.remove(pid_file_path)
            except Exception:
                # Silently ignore deletion errors
                pass

    def exists(self, session_id: str) -> bool:
        """
        Check if a PID file exists for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if the PID file exists, False otherwise
        """
        pid_file_path = self._get_pid_file_path(session_id)
        return os.path.exists(pid_file_path)

    def list_all_session_ids(self) -> list[str]:
        """
        List all session IDs that have PID files.

        Returns:
            List of session IDs (with sanitization reversed)
        """
        if not os.path.exists(self.processes_dir):
            return []

        session_ids = []
        for filename in os.listdir(self.processes_dir):
            if filename.endswith(".pid"):
                # Remove .pid extension to get session_id
                session_id = filename[:-4]
                session_ids.append(session_id)
        return session_ids
