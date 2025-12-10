"""Repository for streaming log file operations."""

from datetime import datetime
from pathlib import Path
from typing import TextIO


class StreamingLogRepository:
    """
    Handles persistence of streaming logs during instruction execution.

    Responsibilities:
    - Open/close log files
    - Write timestamped log entries
    - Ensure proper file flushing for real-time log access

    Note:
    - This is a repository (persistence layer), not a service
    - Business logic for log formatting should be in StreamingLoggerService
    """

    def __init__(self, log_file_path: str):
        """
        Initialize the streaming log repository.

        Args:
            log_file_path: Absolute path to the log file
        """
        self.log_file_path = log_file_path
        self.file_handle: TextIO | None = None

    def open(self) -> None:
        """
        Open the log file in write mode, creating parent directories if needed.

        Note:
        - Creates a new file, overwriting if it exists
        - Parent directories are created automatically
        """
        log_path = Path(self.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.file_handle = open(self.log_file_path, "w", encoding="utf-8")

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
