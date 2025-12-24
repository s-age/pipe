"""Unit tests for StreamingLogRepository."""

import os
import time
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from pipe.core.repositories.streaming_log_repository import StreamingLogRepository

from tests.factories.models.settings_factory import create_test_settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return create_test_settings(timezone="Asia/Tokyo")


@pytest.fixture
def repository(tmp_path, mock_settings):
    """Create a StreamingLogRepository with temporary directory."""
    return StreamingLogRepository(
        project_root=str(tmp_path), session_id="test-session", settings=mock_settings
    )


class TestStreamingLogRepositoryInit:
    """Test StreamingLogRepository initialization."""

    def test_init_sets_paths(self, tmp_path, mock_settings):
        """Test that paths are correctly initialized."""
        repo = StreamingLogRepository(
            project_root=str(tmp_path),
            session_id="test-session",
            settings=mock_settings,
        )
        expected_path = os.path.join(
            str(tmp_path), "sessions", "streaming", "test-session.streaming.log"
        )
        assert repo.log_file_path == expected_path
        assert repo.project_root == str(tmp_path)
        assert repo.session_id == "test-session"

    def test_init_handles_invalid_timezone(self, tmp_path):
        """Test that invalid timezone falls back to UTC."""
        settings = create_test_settings(timezone="Invalid/Timezone")
        repo = StreamingLogRepository(
            project_root=str(tmp_path), session_id="test-session", settings=settings
        )
        assert repo.timezone.key == "UTC"


class TestStreamingLogRepositoryOpenClose:
    """Test StreamingLogRepository open and close methods."""

    def test_open_creates_directories(self, repository):
        """Test that open() creates necessary parent directories."""
        assert not os.path.exists(os.path.dirname(repository.log_file_path))
        repository.open()
        assert os.path.exists(os.path.dirname(repository.log_file_path))
        repository.close()

    def test_open_write_mode(self, repository):
        """Test opening in write mode overwrites existing content."""
        repository.open("w")
        repository.file_handle.write("initial content")
        repository.close()

        repository.open("w")
        repository.close()

        with open(repository.log_file_path, encoding="utf-8") as f:
            assert f.read() == ""

    def test_open_append_mode(self, repository):
        """Test opening in append mode preserves existing content."""
        repository.open("w")
        repository.file_handle.write("initial content")
        repository.close()

        repository.open("a")
        repository.file_handle.write(" appended content")
        repository.close()

        with open(repository.log_file_path, encoding="utf-8") as f:
            assert f.read() == "initial content appended content"

    def test_close_sets_handle_to_none(self, repository):
        """Test that close() sets file_handle to None."""
        repository.open()
        assert repository.file_handle is not None
        repository.close()
        assert repository.file_handle is None

    def test_close_safe_to_call_multiple_times(self, repository):
        """Test that close() can be called multiple times without error."""
        repository.close()
        repository.close()


class TestStreamingLogRepositoryWrite:
    """Test StreamingLogRepository writing methods."""

    def test_write_log_line_success(self, repository):
        """Test writing a log line with explicit timestamp."""
        timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
        repository.open()
        repository.write_log_line("INFO", "Test message", timestamp)
        repository.close()

        with open(repository.log_file_path, encoding="utf-8") as f:
            content = f.read()
            assert "[2025-01-01 12:00:00] INFO: Test message\n" == content

    def test_write_log_line_raises_if_not_open(self, repository):
        """Test that write_log_line raises RuntimeError if file is not open."""
        timestamp = datetime.now(UTC)
        with pytest.raises(RuntimeError, match="Log file is not open"):
            repository.write_log_line("INFO", "Test message", timestamp)

    def test_append_log_auto_opens_and_closes(self, repository):
        """Test append_log handles file opening and closing automatically."""
        repository.append_log("Auto log message", "DEBUG")

        assert repository.file_handle is None
        assert os.path.exists(repository.log_file_path)

        with open(repository.log_file_path, encoding="utf-8") as f:
            content = f.read()
            assert "DEBUG: Auto log message\n" in content

    def test_append_log_stays_open_if_already_open(self, repository):
        """Test append_log doesn't close file if it was already open."""
        repository.open()
        repository.append_log("Message 1")
        assert repository.file_handle is not None
        repository.append_log("Message 2")
        assert repository.file_handle is not None
        repository.close()

        with open(repository.log_file_path, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 2


class TestStreamingLogRepositoryContextManager:
    """Test StreamingLogRepository context manager behavior."""

    def test_context_manager_opens_and_closes(self, repository):
        """Test that 'with' statement opens and closes the file."""
        with repository as repo:
            assert repo.file_handle is not None
            repo.write_log_line("INFO", "Inside context", datetime(2025, 1, 1, 0, 0, 0))

        assert repository.file_handle is None
        assert os.path.exists(repository.log_file_path)


class TestStreamingLogRepositoryDelete:
    """Test StreamingLogRepository delete method."""

    def test_delete_existing_file(self, repository):
        """Test deleting an existing log file."""
        repository.append_log("Test")
        assert os.path.exists(repository.log_file_path)

        result = repository.delete()
        assert result is True
        assert not os.path.exists(repository.log_file_path)

    def test_delete_nonexistent_file(self, repository):
        """Test deleting a non-existent log file."""
        assert not os.path.exists(repository.log_file_path)
        result = repository.delete()
        assert result is False

    def test_delete_closes_handle_first(self, repository):
        """Test that delete() closes the file handle before deleting."""
        repository.open()
        assert repository.file_handle is not None

        result = repository.delete()
        assert result is True
        assert repository.file_handle is None

    @patch("os.remove")
    def test_delete_handles_os_error(self, mock_remove, repository):
        """Test that delete() handles OSError during removal."""
        repository.append_log("Test")
        mock_remove.side_effect = OSError("Permission denied")

        result = repository.delete()
        assert result is False


class TestStreamingLogRepositoryCleanup:
    """Test StreamingLogRepository.cleanup_old_logs static method."""

    def test_cleanup_removes_old_logs(self, tmp_path, mock_settings):
        """Test that cleanup_old_logs removes files older than threshold."""
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)

        # Create an old log file
        old_log = streaming_dir / "old.streaming.log"
        old_log.write_text("old content")
        old_time = time.time() - (40 * 60)  # 40 minutes ago
        os.utime(old_log, (old_time, old_time))

        # Create a new log file
        new_log = streaming_dir / "new.streaming.log"
        new_log.write_text("new content")

        # Create a file with different extension (should be ignored)
        other_file = streaming_dir / "other.txt"
        other_file.write_text("other content")
        os.utime(other_file, (old_time, old_time))

        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), mock_settings, max_age_minutes=30
        )

        assert not old_log.exists()
        assert new_log.exists()
        assert other_file.exists()

    def test_cleanup_handles_missing_directory(self, tmp_path, mock_settings):
        """Test that cleanup_old_logs handles non-existent directory gracefully."""
        # Directory doesn't exist yet
        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), mock_settings, max_age_minutes=30
        )
        # Should not raise any error

    @patch("os.listdir")
    def test_cleanup_handles_os_error_on_listdir(
        self, mock_listdir, tmp_path, mock_settings
    ):
        """Test that cleanup_old_logs handles OSError during listdir."""
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)
        mock_listdir.side_effect = OSError("Access denied")

        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), mock_settings, max_age_minutes=30
        )
        # Should not raise any error

    @patch("os.path.getmtime")
    def test_cleanup_handles_os_error_on_getmtime(
        self, mock_getmtime, tmp_path, mock_settings
    ):
        """Test that cleanup_old_logs handles OSError during getmtime."""
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)
        log_file = streaming_dir / "test.streaming.log"
        log_file.write_text("test")

        mock_getmtime.side_effect = OSError("File not found")

        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), mock_settings, max_age_minutes=30
        )
        # Should not raise any error

    @patch("os.remove")
    def test_cleanup_handles_os_error_on_remove(
        self, mock_remove, tmp_path, mock_settings
    ):
        """Test that cleanup_old_logs handles OSError during remove."""
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)
        log_file = streaming_dir / "old.streaming.log"
        log_file.write_text("old")
        old_time = time.time() - (40 * 60)
        os.utime(log_file, (old_time, old_time))

        mock_remove.side_effect = OSError("Permission denied")

        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), mock_settings, max_age_minutes=30
        )
        # Should not raise any error

    def test_cleanup_handles_invalid_timezone(self, tmp_path):
        """Test cleanup with invalid timezone in settings."""
        settings = create_test_settings(timezone="Invalid/Timezone")
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)

        old_log = streaming_dir / "old.streaming.log"
        old_log.write_text("old content")
        old_time = time.time() - (40 * 60)
        os.utime(old_log, (old_time, old_time))

        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), settings, max_age_minutes=30
        )

        assert not old_log.exists()
