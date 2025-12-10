"""Service for managing streaming log business logic."""

import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pipe.core.repositories.streaming_log_repository import StreamingLogRepository

logger = logging.getLogger(__name__)


class StreamingLoggerService:
    """
    Business logic layer for streaming log management.

    Responsibilities:
    - Coordinate log writing operations
    - Format log entries consistently
    - Provide high-level logging API
    - Manage log lifecycle (start/close)

    Note:
    - This is a service (business logic), not a repository
    - Delegates actual file I/O to StreamingLogRepository
    """

    def __init__(self, repository: "StreamingLogRepository"):
        """
        Initialize the streaming logger service.

        Args:
            repository: StreamingLogRepository for file operations
        """
        self.repository = repository

    def start_logging(self, instruction: str) -> None:
        """
        Start logging and record the initial instruction.

        Args:
            instruction: User instruction that initiated the execution

        Note:
        - Opens the log file via repository
        - Writes the instruction as the first log entry
        """
        self.repository.open()
        self._write_log("INSTRUCTION", instruction)

    def log_chunk(self, chunk: str) -> None:
        """
        Log a streaming chunk from the model.

        Args:
            chunk: Text chunk received from the model

        Note:
        - Used for streaming model responses
        - Each chunk is logged as it arrives
        """
        self._write_log("MODEL_CHUNK", chunk)

    def log_tool_call(self, tool_name: str, args: dict[str, Any]) -> None:
        """
        Log a tool invocation.

        Args:
            tool_name: Name of the tool being called
            args: Arguments passed to the tool

        Note:
        - Arguments are serialized to JSON
        - Format: tool_name({"arg1": "value1", ...})
        """
        try:
            args_str = json.dumps(args, ensure_ascii=False)
            self._write_log("TOOL_CALL", f"{tool_name}({args_str})")
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to serialize tool args for {tool_name}: {e}")
            self._write_log("TOOL_CALL", f"{tool_name}(<serialization failed>)")

    def log_tool_result(self, tool_name: str, result: dict[str, Any]) -> None:
        """
        Log a tool execution result.

        Args:
            tool_name: Name of the tool that was executed
            result: Result dictionary from the tool

        Note:
        - Only logs the status, not the full result (to keep logs concise)
        - Format: tool_name -> status
        """
        status = result.get("status", "unknown")
        self._write_log("TOOL_RESULT", f"{tool_name} -> {status}")

    def log_event(self, event: dict[str, Any]) -> None:
        """
        Log a generic event.

        Args:
            event: Event dictionary to log

        Note:
        - Used for transaction events, state changes, etc.
        - Event is serialized to JSON
        """
        try:
            event_str = json.dumps(event, ensure_ascii=False)
            self._write_log("EVENT", event_str)
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to serialize event: {e}")
            self._write_log("EVENT", "<serialization failed>")

    def log_error(self, error: str) -> None:
        """
        Log an error message.

        Args:
            error: Error message or description
        """
        self._write_log("ERROR", error)

    def close(self) -> None:
        """
        Close the log file with a completion status.

        Note:
        - Writes a final STATUS: COMPLETED entry
        - Closes the repository's file handle
        """
        self._write_log("STATUS", "COMPLETED")
        self.repository.close()

    def _write_log(self, log_type: str, content: str) -> None:
        """
        Internal method to write a log entry with timestamp.

        Args:
            log_type: Type of log entry (e.g., INSTRUCTION, TOOL_CALL)
            content: Content of the log entry

        Note:
        - Automatically adds current timestamp
        - Delegates to repository for actual file I/O
        """
        timestamp = datetime.now()
        try:
            self.repository.write_log_line(log_type, content, timestamp)
        except Exception as e:
            logger.error(f"Failed to write log entry [{log_type}]: {e}")
