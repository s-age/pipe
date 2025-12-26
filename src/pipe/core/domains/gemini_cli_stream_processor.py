"""
Stream processor for Gemini CLI output.

Handles JSON parsing, logging, and session pool management for streaming
responses from the gemini-cli tool.
"""

import json
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pipe.core.repositories.streaming_log_repository import StreamingLogRepository
    from pipe.core.services.session_service import SessionService


class GeminiCliStreamProcessor:
    """
    Processes streaming JSON output from gemini-cli.

    This class handles:
    - Line-by-line JSON parsing
    - Tee-style logging to streaming log repository
    - Extracting assistant messages, tool calls, and tool results
    - Managing session pool updates for tool calls
    """

    def __init__(
        self,
        session_service: "SessionService",
        streaming_log_repo: "StreamingLogRepository | None" = None,
    ):
        """
        Initialize the stream processor.

        Args:
            session_service: Service for session management
            streaming_log_repo: Optional repository for streaming logs
        """
        self.session_service = session_service
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
        except json.JSONDecodeError:
            pass

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
            self._add_tool_call_to_pool(data)

        elif event_type == "tool_result":
            self.tool_results.append(data)

    def _add_tool_call_to_pool(self, tool_call_data: dict) -> None:
        """
        Add a tool call to the session pool if not already present.

        This checks for duplicates from mcp_server.py before adding.

        Args:
            tool_call_data: Tool call data from JSON stream
        """
        from pipe.core.models.turn import FunctionCallingTurn
        from pipe.core.services.session_turn_service import SessionTurnService
        from pipe.core.utils.datetime import get_current_timestamp

        session_id = self.session_service.current_session_id
        if not session_id:
            return

        tool_name = tool_call_data.get("tool_name", "")
        parameters = tool_call_data.get("parameters", {})
        params_json = json.dumps(parameters, ensure_ascii=False)
        response_str = f"{tool_name}({params_json})"
        timestamp = tool_call_data.get(
            "timestamp",
            get_current_timestamp(self.session_service.timezone_obj),
        )

        # Wait briefly for mcp_server.py to write
        time.sleep(0.05)

        # Reload session from file to get latest pools
        session = self.session_service.repository.find(session_id)
        if not session:
            return

        # Check if already exists in recent pool entries (last 5)
        already_exists = False
        recent_pools = session.pools[-5:] if len(session.pools) >= 5 else session.pools
        for pool_entry in recent_pools:
            if (
                hasattr(pool_entry, "type")
                and pool_entry.type == "function_calling"
                and hasattr(pool_entry, "response")
                and pool_entry.response == response_str
            ):
                already_exists = True
                break

        if not already_exists:
            function_calling_turn = FunctionCallingTurn(
                type="function_calling",
                response=response_str,
                timestamp=timestamp,
            )

            session_turn_service = SessionTurnService(
                self.session_service.settings,
                self.session_service.repository,
            )
            session_turn_service.add_to_pool(session_id, function_calling_turn)

    def save_tool_results_to_pool(self) -> None:
        """
        Save all tool calls and results to session pool.

        Only saves if pools is empty (standard tools).
        Skips if mcp_server.py already saved (pipe_tools).
        """
        if not (self.tool_calls or self.tool_results):
            return

        from pipe.core.models.turn import (
            FunctionCallingTurn,
            ToolResponseTurn,
            TurnResponse,
        )
        from pipe.core.utils.datetime import get_current_timestamp

        session_id = self.session_service.current_session_id
        if not session_id:
            return

        # Reload session to check if mcp_server.py added tools to pools
        session = self.session_service.repository.find(session_id)
        if not session:
            return

        # Only add to pools if it's empty (standard tools)
        # If pools has data, mcp_server.py recorded pipe_tools
        if len(session.pools) != 0:
            return

        # Add tool calls
        for tool_call in self.tool_calls:
            tool_name = tool_call.get("tool_name", "")
            parameters = tool_call.get("parameters", {})
            params_json = json.dumps(parameters, ensure_ascii=False)
            response_str = f"{tool_name}({params_json})"
            timestamp = tool_call.get(
                "timestamp",
                get_current_timestamp(self.session_service.timezone_obj),
            )
            turn = FunctionCallingTurn(
                type="function_calling",
                response=response_str,
                timestamp=timestamp,
            )
            session.pools.append(turn)

        # Add tool results
        for tool_result in self.tool_results:
            tool_name = tool_result.get("tool_id", "").split("-")[0]
            status = tool_result.get("status", "failed")
            output = tool_result.get("output", "")
            error = tool_result.get("error")

            if status == "success":
                response = TurnResponse(
                    status="succeeded",
                    message=output,
                )
            else:
                if isinstance(error, dict):
                    error_msg = error.get("message", "")
                else:
                    error_msg = str(error)
                response = TurnResponse(
                    status="failed",
                    message=error_msg,
                )

            timestamp = tool_result.get(
                "timestamp",
                get_current_timestamp(self.session_service.timezone_obj),
            )
            turn = ToolResponseTurn(
                type="tool_response",
                name=tool_name,
                response=response,
                timestamp=timestamp,
            )
            session.pools.append(turn)

        # Save updated session
        self.session_service.repository.save(session)

    def get_result(self) -> dict:
        """
        Get the final processed result.

        Returns:
            Dictionary with response, stats, tool_calls, and tool_results
        """
        return {
            "response": self.assistant_content,
            "stats": self.result_stats,
            "tool_calls": self.tool_calls,
            "tool_results": self.tool_results,
        }
