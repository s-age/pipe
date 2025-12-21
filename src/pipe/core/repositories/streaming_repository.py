"""
Repository for managing streaming logs during session execution.

Handles the persistence of streaming output logs that are written
during agent execution, typically for real-time output tracking.
"""

import os


class StreamingRepository:
    """
    Manages streaming output logs for sessions.

    Each active session can have an associated streaming log file that captures
    real-time output during execution. These logs are separate from the main
    session data and are used for monitoring and debugging.
    """

    def __init__(self, streaming_logs_dir: str):
        """
        Initialize the StreamingRepository.

        Args:
            streaming_logs_dir: Path to the directory where streaming logs are stored
        """
        self.streaming_logs_dir = streaming_logs_dir
        # Ensure streaming logs directory exists
        os.makedirs(self.streaming_logs_dir, exist_ok=True)

    def _get_log_path(self, session_id: str) -> str:
        """
        Get the log file path for a given session.

        Args:
            session_id: The session ID

        Returns:
            The path to the streaming log file
        """
        # Replace slashes in session_id with underscores for filesystem compatibility
        safe_session_id = session_id.replace("/", "__")
        return os.path.join(self.streaming_logs_dir, f"{safe_session_id}.log")

    def append(self, session_id: str, text: str) -> None:
        """
        Append text to a session's streaming log.

        Args:
            session_id: The session ID
            text: The text to append to the log
        """
        log_path = self._get_log_path(session_id)

        # Append to the log file (create if doesn't exist)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")

    def read(self, session_id: str) -> str:
        """
        Read the complete streaming log for a session.

        Args:
            session_id: The session ID

        Returns:
            The complete log content, or empty string if log doesn't exist

        Raises:
            IOError: If there's an error reading the log file
        """
        log_path = self._get_log_path(session_id)

        if not os.path.exists(log_path):
            return ""

        try:
            with open(log_path, encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            raise OSError(f"Failed to read streaming log for session {session_id}: {e}")

    def read_lines(self, session_id: str) -> list[str]:
        """
        Read the streaming log as individual lines.

        Args:
            session_id: The session ID

        Returns:
            List of log lines (without trailing newlines)
        """
        content = self.read(session_id)
        if not content:
            return []
        return content.split("\n")

    def exists(self, session_id: str) -> bool:
        """
        Check if a streaming log exists for a session.

        Args:
            session_id: The session ID

        Returns:
            True if the log file exists, False otherwise
        """
        return os.path.exists(self._get_log_path(session_id))

    def cleanup(self, session_id: str) -> bool:
        """
        Delete a session's streaming log.

        Args:
            session_id: The session ID

        Returns:
            True if the log was deleted, False if it didn't exist
        """
        log_path = self._get_log_path(session_id)

        if os.path.exists(log_path):
            try:
                os.remove(log_path)
                return True
            except OSError as e:
                raise OSError(
                    f"Failed to delete streaming log for session {session_id}: {e}"
                )

        return False

    def cleanup_all(self) -> int:
        """
        Delete all streaming logs.

        Returns:
            The number of log files deleted
        """
        deleted_count = 0

        try:
            for filename in os.listdir(self.streaming_logs_dir):
                if filename.endswith(".log"):
                    log_path = os.path.join(self.streaming_logs_dir, filename)
                    try:
                        os.remove(log_path)
                        deleted_count += 1
                    except OSError:
                        pass  # Continue with other files if one fails

        except OSError:
            pass  # If directory doesn't exist or can't be read, return 0

        return deleted_count
