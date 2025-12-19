"""Service for managing session process lifecycle."""

import json
import logging
import os
import signal
import time
from datetime import UTC
from pathlib import Path
from typing import TYPE_CHECKING

import psutil

if TYPE_CHECKING:
    from pipe.core.models.process_info import ProcessInfo

logger = logging.getLogger(__name__)


class ProcessManagerService:
    """
    Manages process lifecycle for session instruction execution.

    Responsibilities:
    - Register processes when they start
    - Check if processes are running
    - Kill processes when requested
    - Cleanup process information after completion
    - Prevent concurrent execution of the same session

    Note:
    - Uses psutil for reliable process existence checking
    - Stores individual process files in .processes directory
    - No file locking needed - each session has its own file
    """

    def __init__(self, project_root: str):
        """
        Initialize the process manager.

        Args:
            project_root: Root directory of the project
        """
        self.processes_dir = os.path.join(project_root, ".processes")
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

    def _get_process_file_path(self, session_id: str) -> str:
        """
        Get the path to the process file for a session.

        Args:
            session_id: Session identifier

        Returns:
            Path to the process info file
        """
        safe_session_id = self._sanitize_session_id(session_id)
        return os.path.join(self.processes_dir, f"{safe_session_id}.json")

    def _read_process_file(self, session_id: str) -> dict | None:
        """
        Read the process file for a session.

        Args:
            session_id: Session identifier

        Returns:
            Process info dict if found, None otherwise
        """
        process_file = self._get_process_file_path(session_id)
        if not os.path.exists(process_file):
            return None

        try:
            with open(process_file, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(
                f"Failed to read process file for {session_id}: {e}. "
                "Treating as missing."
            )
            return None

    def _write_process_file(self, session_id: str, data: dict) -> None:
        """
        Write the process file for a session atomically.

        Args:
            session_id: Session identifier
            data: Process info data to write

        Note:
        - Uses temp file + rename for atomic writes
        """
        process_file = self._get_process_file_path(session_id)
        temp_path = f"{process_file}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.rename(temp_path, process_file)
        except Exception as e:
            logger.error(f"Failed to write process file for {session_id}: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def _delete_process_file(self, session_id: str) -> None:
        """
        Delete the process file for a session.

        Args:
            session_id: Session identifier
        """
        process_file = self._get_process_file_path(session_id)
        if os.path.exists(process_file):
            try:
                os.remove(process_file)
            except Exception as e:
                logger.warning(f"Failed to delete process file for {session_id}: {e}")

    def register_process(
        self, session_id: str, pid: int, instruction: str
    ) -> None:
        """
        Register a new process for a session.

        Args:
            session_id: Session identifier
            pid: Process ID
            instruction: User instruction that started this process

        Raises:
            RuntimeError: If session is already running
        """
        from datetime import datetime

        from pipe.core.models.process_info import ProcessInfo

        # Check if session is already running
        existing_data = self._read_process_file(session_id)
        if existing_data:
            existing_pid = existing_data["pid"]
            if psutil.pid_exists(existing_pid):
                raise RuntimeError(
                    f"Session {session_id} is already running (PID: {existing_pid})"
                )
            # Process no longer exists, clean it up
            logger.info(f"Cleaning up stale process file for session {session_id}")
            self._delete_process_file(session_id)

        # Register new process
        process_info = ProcessInfo(
            session_id=session_id,
            pid=pid,
            started_at=datetime.now(UTC).isoformat(),
            instruction=instruction,
        )
        self._write_process_file(session_id, process_info.model_dump())

        logger.info(f"Registered process {pid} for session {session_id}")

    def get_process(self, session_id: str) -> "ProcessInfo | None":
        """
        Get process information for a session.

        Args:
            session_id: Session identifier

        Returns:
            ProcessInfo if found, None otherwise
        """
        from pipe.core.models.process_info import ProcessInfo

        process_data = self._read_process_file(session_id)
        if process_data:
            return ProcessInfo(**process_data)
        return None

    def is_running(self, session_id: str) -> bool:
        """
        Check if a process is currently running for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if the process exists and is running, False otherwise

        Note:
        - Uses psutil.pid_exists() for reliable checking
        - Automatically cleans up stale files
        """
        process_data = self._read_process_file(session_id)
        if not process_data:
            return False

        pid = process_data["pid"]
        if psutil.pid_exists(pid):
            return True

        # Process no longer exists, clean it up
        logger.info(f"Auto-cleaning stale process file for session {session_id}")
        self._delete_process_file(session_id)
        return False

    def kill_process(self, session_id: str) -> bool:
        """
        Kill the process associated with a session.

        Args:
            session_id: Session identifier

        Returns:
            True if process was killed successfully, False if not found

        Note:
        - First attempts graceful termination (SIGTERM)
        - Falls back to forceful kill (SIGKILL) after 3 seconds
        - Does not remove from index (use cleanup_process for that)
        """
        process_info = self.get_process(session_id)
        if not process_info:
            logger.warning(f"No process found for session {session_id}")
            return False

        pid = process_info.pid
        if not psutil.pid_exists(pid):
            logger.warning(f"Process {pid} for session {session_id} no longer exists")
            return False

        try:
            # Attempt graceful termination first
            logger.info(f"Sending SIGTERM to process {pid} (session {session_id})")
            os.kill(pid, signal.SIGTERM)

            # Wait up to 3 seconds for graceful shutdown
            for _ in range(30):
                if not psutil.pid_exists(pid):
                    logger.info(f"Process {pid} terminated gracefully")
                    return True
                time.sleep(0.1)

            # Force kill if still running
            logger.warning(
                f"Process {pid} did not terminate gracefully, sending SIGKILL"
            )
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)  # Brief wait for SIGKILL to take effect

            return not psutil.pid_exists(pid)

        except ProcessLookupError:
            logger.info(f"Process {pid} already terminated")
            return True
        except Exception as e:
            logger.error(f"Failed to kill process {pid}: {e}")
            return False

    def cleanup_process(self, session_id: str) -> None:
        """
        Remove process information after completion or termination.

        Args:
            session_id: Session identifier

        Note:
        - Safe to call even if process file doesn't exist
        - Should be called after process completion or termination
        """
        self._delete_process_file(session_id)
        logger.info(f"Cleaned up process file for session {session_id}")

    def cleanup_stale_processes(self) -> None:
        """
        Remove all stale process files from the directory.

        Note:
        - Stale = process ID no longer exists in the system
        - Can be called periodically for maintenance
        """
        if not os.path.exists(self.processes_dir):
            return

        stale_count = 0
        for filename in os.listdir(self.processes_dir):
            if not filename.endswith(".json"):
                continue

            session_id = filename[:-5]  # Remove .json extension
            process_data = self._read_process_file(session_id)

            if process_data and not psutil.pid_exists(process_data["pid"]):
                logger.info(f"Removing stale process file for session {session_id}")
                self._delete_process_file(session_id)
                stale_count += 1

        if stale_count > 0:
            logger.info(f"Cleaned up {stale_count} stale process files")
