"""Repository for streaming log file operations."""

import os
import zoneinfo
from datetime import datetime
from pathlib import Path
from typing import TextIO, cast

from pipe.core.models.settings import Settings
from pipe.core.utils.datetime import get_current_datetime


class StreamingLogRepository:
    """
    Handles persistence of streaming logs during instruction execution.

    Responsibilities:
    - Open/close log files
    - Write timestamped log entries
    - Ensure proper file flushing for real-time log access
    - Manage log file paths and cleanup

    Note:
    - This is a repository (persistence layer), not a service
    - Business logic for log formatting should be in StreamingLoggerService
    """

    def __init__(self, project_root: str, session_id: str, settings: Settings):
        """
        Initialize the streaming log repository.

        Args:
            project_root: Root directory of the project
            session_id: Session identifier for which to manage logs
            settings: Settings object for timezone configuration
        """
        self.project_root = project_root
        self.session_id = session_id
        self.log_file_path = self._build_log_file_path()
        self.file_handle: TextIO | None = None

        # Convert timezone string to ZoneInfo object
        try:
            self.timezone = zoneinfo.ZoneInfo(settings.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            # Fallback to UTC if timezone not found
            self.timezone = zoneinfo.ZoneInfo("UTC")

    def _build_log_file_path(self) -> str:
        """
        Build the log file path from project root and session ID.

        Returns:
            Absolute path to the streaming log file
        """
        return os.path.join(
            self.project_root,
            "sessions",
            "streaming",
            f"{self.session_id}.streaming.log",
        )

    def open(self, mode: str = "w") -> None:
        """
        Open the log file in specified mode, creating parent directories if needed.

        Args:
            mode: File open mode ("w" for write/overwrite, "a" for append)

        Note:
        - "w" mode: Creates a new file, overwriting if it exists
        - "a" mode: Appends to existing file, creates if doesn't exist
        - Parent directories are created automatically
        """
        log_path = Path(self.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.file_handle = cast(
            TextIO, open(self.log_file_path, mode, encoding="utf-8")
        )

    def write_log_line(self, log_type: str, content: str, timestamp: datetime) -> None:
        """
        Write a timestamped log line to the file.

        Args:
            log_type: Type of log entry (e.g., INSTRUCTION, MODEL_CHUNK, TOOL_CALL)
            content: Content of the log entry
            timestamp: Timestamp for this log entry

        Raises:
            RuntimeError: If the log file is not open

        Note:
        - Automatically flushes after each write for real-time viewing
        - Format: [YYYY-MM-DD HH:MM:SS] TYPE: content
        """
        if not self.file_handle:
            raise RuntimeError("Log file is not open. Call open() first.")

        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp_str}] {log_type}: {content}\n"
        self.file_handle.write(log_line)
        self.file_handle.flush()  # Ensure immediate write for real-time access

    def close(self) -> None:
        """
        Close the log file if it's open.

        Note:
        - Safe to call multiple times
        - Sets file_handle to None after closing
        """
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

    def __enter__(self) -> "StreamingLogRepository":
        """
        Context manager entry: opens the log file.

        Returns:
            Self for use in with statement
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit: closes the log file automatically.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.close()

    @staticmethod
    def cleanup_old_logs(
        project_root: str, settings: Settings, max_age_minutes: int = 30
    ) -> None:
        """
        Clean up streaming log files older than max_age_minutes.

        Args:
            project_root: Root directory of the project
            settings: Settings object for timezone configuration
            max_age_minutes: Maximum age of logs in minutes before deletion.
                Defaults to 30.

        Note:
        - Removes log files older than max_age_minutes from sessions/streaming/
        - Silently handles errors to avoid disrupting operations
        """
        streaming_dir = os.path.join(project_root, "sessions", "streaming")
        if not os.path.exists(streaming_dir):
            return

        # Convert timezone string to ZoneInfo object
        try:
            timezone = zoneinfo.ZoneInfo(settings.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            timezone = zoneinfo.ZoneInfo("UTC")

        current_time = get_current_datetime(timezone).timestamp()
        max_age_seconds = max_age_minutes * 60

        try:
            for log_file in os.listdir(streaming_dir):
                if not log_file.endswith(".streaming.log"):
                    continue

                log_file_path = os.path.join(streaming_dir, log_file)
                try:
                    file_mtime = os.path.getmtime(log_file_path)
                    age_seconds = current_time - file_mtime

                    if age_seconds > max_age_seconds:
                        try:
                            os.remove(log_file_path)
                        except OSError:
                            pass
                except OSError:
                    pass

        except OSError:
            pass
