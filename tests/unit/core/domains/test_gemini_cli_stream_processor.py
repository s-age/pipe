import json
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.domains.gemini_cli_stream_processor import (
    GeminiCliStreamProcessor,
    StreamResult,
)


class TestStreamResult:
    """Test cases for the StreamResult dataclass."""

    def test_stream_result_creation(self):
        """Test that a StreamResult object can be created correctly."""
        response = "Hello"
        tool_calls = [{"tool_code": "print('hello')"}]
        tool_results = [{"result": "None"}]
        stats = {"tokens": 10, "cost": 0.01}

        result = StreamResult(
            response=response,
            tool_calls=tool_calls,
            tool_results=tool_results,
            stats=stats,
        )

        assert result.response == response
        assert result.tool_calls == tool_calls
        assert result.tool_results == tool_results
        assert result.stats == stats

    def test_stream_result_empty_fields(self):
        """Test StreamResult creation with empty lists and None stats."""
        result = StreamResult(
            response="",
            tool_calls=[],
            tool_results=[],
            stats=None,
        )
        assert result.response == ""
        assert result.tool_calls == []
        assert result.tool_results == []
        assert result.stats is None


class TestGeminiCliStreamProcessor:
    """Test cases for the GeminiCliStreamProcessor class."""

    @pytest.fixture
    def mock_streaming_log_repo(self):
        """Fixture for a mock StreamingLogRepository."""
        return MagicMock()

    @pytest.fixture
    def processor_no_repo(self):
        """Fixture for a processor without a streaming log repository."""
        return GeminiCliStreamProcessor()

    @pytest.fixture
    def processor_with_repo(self, mock_streaming_log_repo):
        """Fixture for a processor with a mock streaming log repository."""
        return GeminiCliStreamProcessor(streaming_log_repo=mock_streaming_log_repo)

    def test_init_no_repo(self, processor_no_repo):
        """Test initialization without a streaming log repository."""
        assert processor_no_repo.streaming_log_repo is None
        assert processor_no_repo.assistant_content == ""
        assert processor_no_repo.tool_calls == []
        assert processor_no_repo.tool_results == []
        assert processor_no_repo.result_stats is None

    def test_init_with_repo(self, processor_with_repo, mock_streaming_log_repo):
        """Test initialization with a mock streaming log repository."""
        assert processor_with_repo.streaming_log_repo == mock_streaming_log_repo
        assert processor_with_repo.assistant_content == ""
        assert processor_with_repo.tool_calls == []
        assert processor_with_repo.tool_results == []
        assert processor_with_repo.result_stats is None

    @patch("builtins.print")
    def test_process_line_message_event(self, mock_print, processor_no_repo):
        """Test processing a line with an assistant message event."""
        line = json.dumps({"type": "message", "role": "assistant", "content": "Hello"})
        processor_no_repo.process_line(line)

        assert processor_no_repo.assistant_content == "Hello"
        assert not processor_no_repo.tool_calls
        assert not processor_no_repo.tool_results
        assert processor_no_repo.result_stats is None
        mock_print.assert_called_once_with(line)

    @patch("builtins.print")
    def test_process_line_result_event(self, mock_print, processor_no_repo):
        """Test processing a line with a result event (stats)."""
        stats_data = {"tokens": 10, "cost": 0.01}
        line = json.dumps({"type": "result", "stats": stats_data})
        processor_no_repo.process_line(line)

        assert processor_no_repo.assistant_content == ""
        assert not processor_no_repo.tool_calls
        assert not processor_no_repo.tool_results
        assert processor_no_repo.result_stats == stats_data
        mock_print.assert_called_once_with(line)

    @patch("builtins.print")
    def test_process_line_tool_use_event(self, mock_print, processor_no_repo):
        """Test processing a line with a tool_use event."""
        tool_use_data = {"type": "tool_use", "tool_code": "tool_call()"}
        line = json.dumps(tool_use_data)
        processor_no_repo.process_line(line)

        assert processor_no_repo.assistant_content == ""
        assert processor_no_repo.tool_calls == [tool_use_data]
        assert not processor_no_repo.tool_results
        assert processor_no_repo.result_stats is None
        mock_print.assert_called_once_with(line)

    @patch("builtins.print")
    def test_process_line_tool_result_event(self, mock_print, processor_no_repo):
        """Test processing a line with a tool_result event."""
        tool_result_data = {"type": "tool_result", "result": "success"}
        line = json.dumps(tool_result_data)
        processor_no_repo.process_line(line)

        assert processor_no_repo.assistant_content == ""
        assert not processor_no_repo.tool_calls
        assert processor_no_repo.tool_results == [tool_result_data]
        assert processor_no_repo.result_stats is None
        mock_print.assert_called_once_with(line)

    @patch("builtins.print")
    def test_process_line_multiple_events(self, mock_print, processor_no_repo):
        """Test processing multiple lines with different events."""
        line1 = json.dumps({"type": "message", "role": "assistant", "content": "Part1"})
        line2 = json.dumps({"type": "tool_use", "tool_code": "tool1()"})
        line3 = json.dumps(
            {"type": "message", "role": "assistant", "content": " Part2"}
        )
        line4 = json.dumps({"type": "tool_result", "result": "tool1_success"})
        line5 = json.dumps({"type": "result", "stats": {"tokens": 20}})

        processor_no_repo.process_line(line1)
        processor_no_repo.process_line(line2)
        processor_no_repo.process_line(line3)
        processor_no_repo.process_line(line4)
        processor_no_repo.process_line(line5)

        assert processor_no_repo.assistant_content == "Part1 Part2"
        assert len(processor_no_repo.tool_calls) == 1
        assert len(processor_no_repo.tool_results) == 1
        assert processor_no_repo.result_stats == {"tokens": 20}
        assert mock_print.call_count == 5

    @patch("builtins.print")
    def test_process_line_invalid_json_with_repo(
        self, mock_print, processor_with_repo, mock_streaming_log_repo
    ):
        """Test processing a line with invalid JSON, verify error logging."""
        invalid_line = "this is not json"
        processor_with_repo.process_line(invalid_line)

        mock_print.assert_called_once_with(invalid_line)
        mock_streaming_log_repo.append_log.assert_any_call(invalid_line, "STREAM")
        mock_streaming_log_repo.append_log.assert_any_call(
            f"JSON parse error: Expecting value: line 1 column 1 (char 0) | Line: {invalid_line}",
            "ERROR",
        )
        assert processor_with_repo.assistant_content == ""
        assert not processor_with_repo.tool_calls
        assert not processor_with_repo.tool_results
        assert processor_with_repo.result_stats is None

    @patch("builtins.print")
    def test_process_line_invalid_json_no_repo(self, mock_print, processor_no_repo):
        """Test processing a line with invalid JSON when no repo is present."""
        invalid_line = "this is not json"
        processor_no_repo.process_line(invalid_line)

        mock_print.assert_called_once_with(invalid_line)
        assert processor_no_repo.assistant_content == ""
        assert not processor_no_repo.tool_calls
        assert not processor_no_repo.tool_results
        assert processor_no_repo.result_stats is None

    @patch("builtins.print")
    def test_process_line_empty_line(self, mock_print, processor_no_repo):
        """Test processing an empty line."""
        empty_line = ""
        processor_no_repo.process_line(empty_line)

        mock_print.assert_called_once_with(empty_line)
        assert processor_no_repo.assistant_content == ""
        assert not processor_no_repo.tool_calls
        assert not processor_no_repo.tool_results
        assert processor_no_repo.result_stats is None

    @patch("builtins.print")
    def test_process_line_with_streaming_log_repo(
        self, mock_print, processor_with_repo, mock_streaming_log_repo
    ):
        """Test that append_log is called when streaming_log_repo is provided."""
        line = json.dumps({"type": "message", "role": "assistant", "content": "Test"})
        processor_with_repo.process_line(line)

        mock_print.assert_called_once_with(line)
        mock_streaming_log_repo.append_log.assert_called_once_with(line, "STREAM")

    def test_get_result_empty(self, processor_no_repo):
        """Test get_result when no lines have been processed."""
        result = processor_no_repo.get_result()
        assert result.response == ""
        assert result.tool_calls == []
        assert result.tool_results == []
        assert result.stats is None

    def test_get_result_after_processing_multiple_events(self, processor_no_repo):
        """Test get_result after processing various events."""
        line1 = json.dumps(
            {"type": "message", "role": "assistant", "content": "Final "}
        )
        line2 = json.dumps({"type": "tool_use", "tool_code": "final_tool()"})
        line3 = json.dumps(
            {"type": "message", "role": "assistant", "content": "Content"}
        )
        line4 = json.dumps({"type": "tool_result", "result": "final_success"})
        line5 = json.dumps({"type": "result", "stats": {"final_tokens": 30}})

        processor_no_repo.process_line(line1)
        processor_no_repo.process_line(line2)
        processor_no_repo.process_line(line3)
        processor_no_repo.process_line(line4)
        processor_no_repo.process_line(line5)

        result = processor_no_repo.get_result()
        assert result.response == "Final Content"
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["tool_code"] == "final_tool()"
        assert len(result.tool_results) == 1
        assert result.tool_results[0]["result"] == "final_success"
        assert result.stats == {"final_tokens": 30}

    def test_get_result_accumulates_assistant_content(self, processor_no_repo):
        """Test that assistant content is accumulated correctly."""
        line1 = json.dumps(
            {"type": "message", "role": "assistant", "content": "First part. "}
        )
        line2 = json.dumps(
            {"type": "message", "role": "assistant", "content": "Second part."}
        )

        processor_no_repo.process_line(line1)
        processor_no_repo.process_line(line2)

        result = processor_no_repo.get_result()
        assert result.response == "First part. Second part."
        assert not result.tool_calls
        assert not result.tool_results
        assert result.stats is None

    def test_handle_json_event_unknown_type(self, processor_no_repo):
        """Test _handle_json_event with an unknown event type."""
        data = {"type": "unknown_event", "payload": "some_data"}
        processor_no_repo._handle_json_event(data)

        assert processor_no_repo.assistant_content == ""
        assert not processor_no_repo.tool_calls
        assert not processor_no_repo.tool_results
        assert processor_no_repo.result_stats is None

    def test_handle_json_event_message_non_assistant_role(self, processor_no_repo):
        """Test _handle_json_event with a message event but non-assistant role."""
        data = {"type": "message", "role": "user", "content": "User message"}
        processor_no_repo._handle_json_event(data)

        assert processor_no_repo.assistant_content == ""
        assert not processor_no_repo.tool_calls
        assert not processor_no_repo.tool_results
        assert processor_no_repo.result_stats is None
