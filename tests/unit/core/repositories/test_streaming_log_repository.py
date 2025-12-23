"""Unit tests for StreamingLogRepository."""

import os
import zoneinfo
from datetime import datetime
from unittest.mock import patch

import pytest
from pipe.core.repositories.streaming_log_repository import StreamingLogRepository

from tests.factories.models.settings_factory import create_test_settings


@pytest.fixture
def mock_settings():
    """Create test settings."""
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
            project_root=str(tmp_path), session_id="abc-123", settings=mock_settings
        )
        assert repo.project_root == str(tmp_path)
        assert repo.session_id == "abc-123"
        assert repo.log_file_path == os.path.join(
            str(tmp_path), "sessions", "streaming", "abc-123.streaming.log"
        )
        assert repo.file_handle is None
        assert repo.timezone == zoneinfo.ZoneInfo("Asia/Tokyo")

    def test_init_fallback_to_utc(self, tmp_path):
        """Test fallback to UTC if timezone is invalid."""
        settings = create_test_settings(timezone="Invalid/Timezone")
        repo = StreamingLogRepository(
            project_root=str(tmp_path), session_id="test", settings=settings
        )
        assert repo.timezone == zoneinfo.ZoneInfo("UTC")


class TestStreamingLogRepositoryOpenClose:
    """Test StreamingLogRepository.open() and close() methods."""

    def test_open_creates_directories_and_file(self, repository):
        """Test that open() creates the necessary directory structure."""
        repository.open()
        assert repository.file_handle is not None
        assert os.path.exists(repository.log_file_path)
        repository.close()

    def test_open_append_mode(self, repository):
        """Test opening in append mode."""
        repository.open("w")
        repository.file_handle.write("line 1\n")
        repository.close()

        repository.open("a")
        repository.file_handle.write("line 2\n")
        repository.close()

        with open(repository.log_file_path) as f:
            content = f.read()
        assert content == "line 1\nline 2\n"

    def test_close_multiple_times(self, repository):
        """Test that close() can be called safely multiple times."""
        repository.open()
        repository.close()
        repository.close()  # Should not raise error
        assert repository.file_handle is None


class TestStreamingLogRepositoryWrite:
    """Test StreamingLogRepository.write_log_line() method."""

    def test_write_log_line_format(self, repository):
        """Test that log lines are formatted correctly."""
        timestamp = datetime(2025, 12, 23, 10, 0, 0)
        repository.open()
        repository.write_log_line("TYPE", "Some content", timestamp)
        repository.close()

        with open(repository.log_file_path) as f:
            line = f.read()
        assert line == "[2025-12-23 10:00:00] TYPE: Some content\n"

    def test_write_log_line_not_open_raises_error(self, repository):
        """Test that write_log_line() raises RuntimeError if file is not open."""
        timestamp = datetime.now()
        with pytest.raises(RuntimeError, match="Log file is not open"):
            repository.write_log_line("ERR", "content", timestamp)

    def test_write_log_line_flushes_immediately(self, repository):
        """Test that write_log_line() flushes content immediately."""
        timestamp = datetime.now()
        repository.open()
        repository.write_log_line("TYPE", "content", timestamp)

        # Read from the file while it's still open
        with open(repository.log_file_path) as f:
            content = f.read()
        assert "TYPE: content" in content
        repository.close()


class TestStreamingLogRepositoryContextManager:
    """Test context manager support."""

    def test_context_manager(self, repository):
        """Test that with statement opens and closes file."""
        with repository as repo:
            assert repo.file_handle is not None
            repo.write_log_line("CM", "test", datetime(2025, 1, 1, 0, 0, 0))

        assert repository.file_handle is None
        with open(repository.log_file_path) as f:
            content = f.read()
        assert "[2025-01-01 00:00:00] CM: test\n" == content


class TestStreamingLogRepositoryCleanup:
    """Test StreamingLogRepository.cleanup_old_logs() method."""

    def test_cleanup_removes_old_files(self, tmp_path, mock_settings):
        """Test that old logs are removed."""
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)

        old_file = streaming_dir / "old.streaming.log"
        new_file = streaming_dir / "new.streaming.log"

        old_file.write_text("old content")
        new_file.write_text("new content")

        # Set mtime for old file to 40 minutes ago
        current_time = datetime.now().timestamp()
        os.utime(old_file, (current_time - 40 * 60, current_time - 40 * 60))

        # We need to mock get_current_datetime to return a fixed current time
        # because the implementation uses it to compare with mtime
        with patch(
            "pipe.core.repositories.streaming_log_repository.get_current_datetime"
        ) as mock_get_now:
            mock_get_now.return_value = datetime.fromtimestamp(current_time)

            StreamingLogRepository.cleanup_old_logs(
                str(tmp_path), mock_settings, max_age_minutes=30
            )

        assert not old_file.exists()
        assert new_file.exists()

    def test_cleanup_ignores_non_log_files(self, tmp_path, mock_settings):
        """Test that non-log files are ignored."""
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)

        other_file = streaming_dir / "other.txt"
        other_file.write_text("content")

        current_time = datetime.now().timestamp()
        os.utime(other_file, (current_time - 40 * 60, current_time - 40 * 60))

        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), mock_settings, max_age_minutes=30
        )

        assert other_file.exists()

    def test_cleanup_no_directory(self, tmp_path, mock_settings):
        """Test cleanup when streaming directory doesn't exist."""
        # Should not raise any error
        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), mock_settings, max_age_minutes=30
        )

    def test_cleanup_handles_invalid_timezone(self, tmp_path):
        """Test cleanup handles invalid timezone in settings."""
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)
        log_file = streaming_dir / "test.streaming.log"
        log_file.write_text("test")

        settings = create_test_settings(timezone="Invalid/Zone")
        # Should not raise any error
        StreamingLogRepository.cleanup_old_logs(
            str(tmp_path), settings, max_age_minutes=30
        )
        assert log_file.exists()

    def test_cleanup_handles_os_errors(self, tmp_path, mock_settings):
        """Test that cleanup_old_logs handles OSError gracefully."""
        streaming_dir = tmp_path / "sessions" / "streaming"
        streaming_dir.mkdir(parents=True)
        log_file = streaming_dir / "error.streaming.log"
        log_file.write_text("test")

        # Mock os.path.getmtime to raise OSError
        with patch("os.path.getmtime", side_effect=OSError("Access denied")):
            StreamingLogRepository.cleanup_old_logs(
                str(tmp_path), mock_settings, max_age_minutes=30
            )
            # Should not raise exception and file should still exist
            assert log_file.exists()

        # Mock os.remove to raise OSError
        current_time = datetime.now().timestamp()
        os.utime(log_file, (current_time - 40 * 60, current_time - 40 * 60))
        with patch("os.remove", side_effect=OSError("Permission denied")):
            StreamingLogRepository.cleanup_old_logs(
                str(tmp_path), mock_settings, max_age_minutes=30
            )
            # Should not raise exception and file should still exist
            assert log_file.exists()

        # Mock os.listdir to raise OSError
        with patch("os.listdir", side_effect=OSError("Disk error")):
            StreamingLogRepository.cleanup_old_logs(
                str(tmp_path), mock_settings, max_age_minutes=30
            )
            # Should not raise exception
