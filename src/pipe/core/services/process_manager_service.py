"""Service for managing session process lifecycle."""

import logging
import os
import signal
import time

import psutil
from pipe.core.repositories.process_file_repository import ProcessFileRepository

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
    - Delegates file I/O to ProcessFileRepository
    - Stores only PID in simple .pid files
    """

    def __init__(self, project_root: str):
        """
        Initialize the process manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        processes_dir = os.path.join(project_root, ".processes")
        self.repository = ProcessFileRepository(processes_dir)

    def register_process(self, session_id: str, pid: int) -> None:
        """
        Register a new process for a session.

        Args:
            session_id: Session identifier
            pid: Process ID

        Raises:
            RuntimeError: If session is already running
        """
        # Check if session is already running
        existing_pid = self.repository.read_pid(session_id)
        if existing_pid is not None:
            if psutil.pid_exists(existing_pid):
                raise RuntimeError(
                    f"Session {session_id} is already running (PID: {existing_pid})"
                )
            # Process no longer exists, clean it up
            logger.info(f"Cleaning up stale process file for session {session_id}")
            self.repository.delete_pid_file(session_id)

        # Register new process
        self.repository.write_pid(session_id, pid)
        logger.info(f"Registered process {pid} for session {session_id}")

    def get_pid(self, session_id: str) -> int | None:
        """
        Get process ID for a session.

        Args:
            session_id: Session identifier

        Returns:
            PID if found, None otherwise
        """
        return self.repository.read_pid(session_id)

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
        pid = self.repository.read_pid(session_id)
        if pid is None:
            return False

        if psutil.pid_exists(pid):
            return True

        # Process no longer exists, clean it up
        logger.info(f"Auto-cleaning stale process file for session {session_id}")
        self.repository.delete_pid_file(session_id)
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
        pid = self.get_pid(session_id)
        if pid is None:
            logger.warning(f"No process found for session {session_id}")
            return False

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
        self.repository.delete_pid_file(session_id)
        logger.info(f"Cleaned up process file for session {session_id}")

    def cleanup_stale_processes(self) -> None:
        """
        Remove all stale process files from the directory.

        Note:
        - Stale = process ID no longer exists in the system
        - Can be called periodically for maintenance
        """
        stale_count = 0
        for session_id in self.repository.list_all_session_ids():
            pid = self.repository.read_pid(session_id)
            if pid is not None and not psutil.pid_exists(pid):
                logger.info(f"Removing stale process file for session {session_id}")
                self.repository.delete_pid_file(session_id)
                stale_count += 1

        if stale_count > 0:
            logger.info(f"Cleaned up {stale_count} stale process files")
