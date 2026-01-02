"""Unit tests for StreamingLoggerService."""

import json
import zoneinfo
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from pipe.core.models.settings import Settings
from pipe.core.services.streaming_logger_service import StreamingLoggerService


@pytest.fixture
def mock_repository():
    """Create a mock StreamingLogRepository."""
    # We don't import StreamingLogRepository at runtime to avoid circular imports
    # if it were to happen, and because it's only used for type checking in the service.
    # However, for spec= we need the class.
    mock_repo = MagicMock()
    return mock_repo


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock(spec=Settings)
    settings.timezone = "Asia/Tokyo"
    return settings


@pytest.fixture
def service(mock_repository, mock_settings):
    """Create StreamingLoggerService instance."""
    return StreamingLoggerService(repository=mock_repository, settings=mock_settings)


class TestStreamingLoggerServiceInit:
    """Tests for StreamingLoggerService.__init__."""

    def test_init_valid_timezone(self, mock_repository):
        """Test initialization with a valid timezone."""
        settings = MagicMock(spec=Settings)
        settings.timezone = "Asia/Tokyo"

        service = StreamingLoggerService(mock_repository, settings)

        assert service.timezone == zoneinfo.ZoneInfo("Asia/Tokyo")
        assert service.repository == mock_repository

    def test_init_invalid_timezone(self, mock_repository):
        """Test initialization with an invalid timezone falls back to UTC."""
        settings = MagicMock(spec=Settings)
        settings.timezone = "Invalid/Timezone"

        service = StreamingLoggerService(mock_repository, settings)

        assert service.timezone == zoneinfo.ZoneInfo("UTC")


class TestStreamingLoggerServiceOpen:
    """Tests for StreamingLoggerService.open."""

    def test_open_default(self, service, mock_repository):
        """Test open with default mode."""
        service.open()
        mock_repository.open.assert_called_once_with("w")

    def test_open_custom_mode(self, service, mock_repository):
        """Test open with custom mode."""
        service.open(mode="a")
        mock_repository.open.assert_called_once_with("a")


class TestStreamingLoggerServiceStartLogging:
    """Tests for StreamingLoggerService.start_logging."""

    def test_start_logging(self, service, mock_repository):
        """Test start_logging opens repository and writes instruction."""
        with patch.object(service, "_write_log") as mock_write_log:
            service.start_logging("Test instruction")

            mock_repository.open.assert_called_once()
            mock_write_log.assert_called_once_with("INSTRUCTION", "Test instruction")


class TestStreamingLoggerServiceLogChunk:
    """Tests for StreamingLoggerService.log_chunk."""

    def test_log_chunk(self, service):
        """Test log_chunk calls _write_log."""
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_chunk("chunk content")
            mock_write_log.assert_called_once_with("MODEL_CHUNK", "chunk content")


class TestStreamingLoggerServiceLogRawChunk:
    """Tests for StreamingLoggerService.log_raw_chunk."""

    def test_log_raw_chunk_success(self, service):
        """Test log_raw_chunk serializes data and calls _write_log."""
        chunk_data = {"text": "hello", "usage": {"tokens": 10}}
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_raw_chunk(chunk_data)

            expected_json = json.dumps(chunk_data, ensure_ascii=False)
            mock_write_log.assert_called_once_with("RAW_CHUNK", expected_json)

    def test_log_raw_chunk_serialization_failure(self, service):
        """Test log_raw_chunk handles serialization failure."""
        # Object that cannot be serialized to JSON
        chunk_data = {"error": object()}
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_raw_chunk(chunk_data)
            mock_write_log.assert_called_once_with(
                "RAW_CHUNK", "<serialization failed>"
            )


class TestStreamingLoggerServiceLogToolCall:
    """Tests for StreamingLoggerService.log_tool_call."""

    def test_log_tool_call_success(self, service):
        """Test log_tool_call serializes args and calls _write_log."""
        args = {"path": "test.py", "content": "print('hi')"}
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_tool_call("write_file", args)

            args_json = json.dumps(args, ensure_ascii=False)
            mock_write_log.assert_called_once_with(
                "TOOL_CALL", f"write_file({args_json})"
            )

    def test_log_tool_call_serialization_failure(self, service):
        """Test log_tool_call handles serialization failure."""
        args = {"bad": object()}
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_tool_call("write_file", args)
            mock_write_log.assert_called_once_with(
                "TOOL_CALL", "write_file(<serialization failed>)"
            )


class TestStreamingLoggerServiceLogToolResult:
    """Tests for StreamingLoggerService.log_tool_result."""

    def test_log_tool_result_with_status(self, service):
        """Test log_tool_result extracts status and calls _write_log."""
        result = {"status": "succeeded", "output": "done"}
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_tool_result("write_file", result)
            mock_write_log.assert_called_once_with(
                "TOOL_RESULT", "write_file -> succeeded"
            )

    def test_log_tool_result_without_status(self, service):
        """Test log_tool_result uses 'unknown' if status is missing."""
        result = {"output": "done"}
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_tool_result("write_file", result)
            mock_write_log.assert_called_once_with(
                "TOOL_RESULT", "write_file -> unknown"
            )


class TestStreamingLoggerServiceLogEvent:
    """Tests for StreamingLoggerService.log_event."""

    def test_log_event_success(self, service):
        """Test log_event serializes event and calls _write_log."""
        event = {"type": "transaction", "id": "123"}
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_event(event)

            event_json = json.dumps(event, ensure_ascii=False)
            mock_write_log.assert_called_once_with("EVENT", event_json)

    def test_log_event_serialization_failure(self, service):
        """Test log_event handles serialization failure."""
        event = {"bad": object()}
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_event(event)
            mock_write_log.assert_called_once_with("EVENT", "<serialization failed>")


class TestStreamingLoggerServiceLogError:
    """Tests for StreamingLoggerService.log_error."""

    def test_log_error(self, service):
        """Test log_error calls _write_log."""
        with patch.object(service, "_write_log") as mock_write_log:
            service.log_error("Something went wrong")
            mock_write_log.assert_called_once_with("ERROR", "Something went wrong")


class TestStreamingLoggerServiceClose:
    """Tests for StreamingLoggerService.close."""

    def test_close(self, service, mock_repository):
        """Test close writes status and closes repository."""
        with patch.object(service, "_write_log") as mock_write_log:
            service.close()

            mock_write_log.assert_called_once_with("STATUS", "COMPLETED")
            mock_repository.close.assert_called_once()


class TestStreamingLoggerServiceWriteLog:
    """Tests for StreamingLoggerService._write_log."""

    @freeze_time("2025-01-01 12:00:00")
    def test_write_log_success(self, service, mock_repository):
        """Test _write_log calls repository.write_log_line with correct arguments."""
        # service.timezone is Asia/Tokyo (UTC+9) from mock_settings fixture
        # 2025-01-01 12:00:00 UTC -> 2025-01-01 21:00:00 JST

        service._write_log("TEST_TYPE", "test content")

        # Verify get_current_datetime was called with service.timezone
        # We can't easily verify the exact datetime object passed to write_log_line
        # because it's created inside the method, but freeze_time handles it.

        args, kwargs = mock_repository.write_log_line.call_args
        assert args[0] == "TEST_TYPE"
        assert args[1] == "test content"
        # args[2] is the timestamp
        assert args[2].year == 2025
        assert args[2].month == 1
        assert args[2].day == 1
        assert args[2].hour == 21  # JST
        assert args[2].tzinfo == zoneinfo.ZoneInfo("Asia/Tokyo")

    def test_write_log_repository_error(self, service, mock_repository):
        """Test _write_log handles repository exceptions gracefully."""
        mock_repository.write_log_line.side_effect = Exception("Write failed")

        # Should not raise exception
        with patch("pipe.core.services.streaming_logger_service.logger") as mock_logger:
            service._write_log("TEST_TYPE", "test content")
            mock_logger.error.assert_called_once()
