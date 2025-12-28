"""
Stream processor for Gemini CLI output.

Handles JSON parsing and logging for streaming responses from the gemini-cli tool.
This is a pure parser with no file I/O responsibilities.
"""

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pipe.core.repositories.streaming_log_repository import StreamingLogRepository


@dataclass
class StreamResult:
    """Result of parsing gemini-cli JSON stream."""

    response: str  # Accumulated assistant content
    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    stats: dict[str, Any] | None


class GeminiCliStreamProcessor:
    """
    Processes streaming JSON output from gemini-cli.

    This class handles:
    - Line-by-line JSON parsing
    - Tee-style logging to streaming log repository
    - Extracting assistant messages, tool calls, and tool results

    This is a pure parser with no session file I/O responsibilities.
    """

    def __init__(
        self,
        streaming_log_repo: "StreamingLogRepository | None" = None,
    ):
        """
        Initialize the stream processor.

        Args:
            streaming_log_repo: Optional repository for streaming logs
        """
        self.streaming_log_repo = streaming_log_repo
        self.assistant_content = ""
        self.tool_calls: list[dict] = []
        self.tool_results: list[dict] = []
        self.result_stats: dict[str, Any] | None = None

    def process_line(self, line: str) -> None:
        """
        Process a single line of JSON output from gemini-cli.

        Args:
            line: A line of JSON output
        """
        # Print to stdout
        print(line.strip())

        # Log to streaming repository
        if self.streaming_log_repo:
            self.streaming_log_repo.append_log(line.strip(), "STREAM")

        # Parse and extract data
        try:
            data = json.loads(line.strip())
            self._handle_json_event(data)
        except json.JSONDecodeError as e:
            if self.streaming_log_repo:
                self.streaming_log_repo.append_log(
                    f"JSON parse error: {e} | Line: {line.strip()}", "ERROR"
                )

    def _handle_json_event(self, data: dict) -> None:
        """
        Handle a parsed JSON event from gemini-cli.

        Args:
            data: Parsed JSON object
        """
        event_type = data.get("type")

        if event_type == "message" and data.get("role") == "assistant":
            self.assistant_content += data.get("content", "")

        elif event_type == "result":
            self.result_stats = data.get("stats")

        elif event_type == "tool_use":
            self.tool_calls.append(data)

        elif event_type == "tool_result":
            self.tool_results.append(data)

    def get_result(self) -> StreamResult:
        """
        Get the final processed result.

        Returns:
            StreamResult dataclass with response, stats, tool_calls, and tool_results
        """
        return StreamResult(
            response=self.assistant_content,
            tool_calls=self.tool_calls,
            tool_results=self.tool_results,
            stats=self.result_stats,
        )
