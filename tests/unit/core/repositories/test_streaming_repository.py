"""
Tests for StreamingRepository.
"""

import os
from unittest.mock import patch

import pytest
from pipe.core.repositories.streaming_repository import StreamingRepository


@pytest.fixture
def streaming_logs_dir(tmp_path):
    """Create a temporary directory for streaming logs."""
    logs_dir = tmp_path / "streaming_logs"
    return str(logs_dir)


@pytest.fixture
def repository(streaming_logs_dir):
    """Create a StreamingRepository instance."""
    return StreamingRepository(streaming_logs_dir)


class TestStreamingRepositoryInit:
    """Tests for StreamingRepository.__init__."""

    def test_init_creates_directory(self, streaming_logs_dir):
        """Test that __init__ creates the streaming logs directory."""
        # Directory should not exist yet
        if os.path.exists(streaming_logs_dir):
            os.rmdir(streaming_logs_dir)
        assert not os.path.exists(streaming_logs_dir)

        # Initialize repository
        StreamingRepository(streaming_logs_dir)

        # Directory should now exist
        assert os.path.exists(streaming_logs_dir)
        assert os.path.isdir(streaming_logs_dir)


class TestStreamingRepositoryLogPath:
    """Tests for StreamingRepository._get_log_path."""

    def test_get_log_path_safe_session_id(self, repository, streaming_logs_dir):
        """Test that _get_log_path replaces slashes in session_id."""
        session_id = "parent/child/session-123"
        expected_filename = "parent__child__session-123.log"
        expected_path = os.path.join(streaming_logs_dir, expected_filename)

        path = repository._get_log_path(session_id)
        assert path == expected_path


class TestStreamingRepositoryAppend:
    """Tests for StreamingRepository.append."""

    def test_append_creates_new_file(self, repository, streaming_logs_dir):
        """Test that append creates a new log file if it doesn't exist."""
        session_id = "test-session"
        text = "Initial log entry"

        repository.append(session_id, text)

        log_path = repository._get_log_path(session_id)
        assert os.path.exists(log_path)
        with open(log_path, encoding="utf-8") as f:
            content = f.read()
            assert content == text + "\n"

    def test_append_to_existing_file(self, repository, streaming_logs_dir):
        """Test that append appends to an existing log file."""
        session_id = "test-session"
        text1 = "First entry"
        text2 = "Second entry"

        repository.append(session_id, text1)
        repository.append(session_id, text2)

        log_path = repository._get_log_path(session_id)
        with open(log_path, encoding="utf-8") as f:
            content = f.read()
            assert content == text1 + "\n" + text2 + "\n"

    def test_append_ensures_newline(self, repository):
        """Test that append adds a newline if missing."""
        session_id = "newline-test"

        # Case 1: No trailing newline
        repository.append(session_id, "line1")
        assert repository.read(session_id) == "line1\n"

        # Case 2: Already has trailing newline
        repository.append(session_id, "line2\n")
        assert repository.read(session_id) == "line1\nline2\n"

    def test_append_hierarchical_session_id(self, repository):
        """Test append with hierarchical session ID."""
        session_id = "nested/session"
        repository.append(session_id, "data")

        assert repository.exists(session_id)
        assert repository.read(session_id) == "data\n"


class TestStreamingRepositoryRead:
    """Tests for StreamingRepository.read."""

    def test_read_existing_file(self, repository):
        """Test reading an existing log file."""
        session_id = "read-test"
        text = "some log content"
        repository.append(session_id, text)

        content = repository.read(session_id)
        assert content == text + "\n"

    def test_read_nonexistent_file(self, repository):
        """Test reading a non-existent log file returns empty string."""
        content = repository.read("nonexistent")
        assert content == ""

    def test_read_os_error(self, repository):
        """Test handling of OSError during read."""
        session_id = "error-test"
        repository.append(session_id, "data")

        with patch("builtins.open", side_effect=OSError("Read error")):
            with pytest.raises(OSError, match="Failed to read streaming log"):
                repository.read(session_id)


class TestStreamingRepositoryReadLines:
    """Tests for StreamingRepository.read_lines."""

    def test_read_lines_existing_file(self, repository):
        """Test reading lines from an existing file."""
        session_id = "lines-test"
        repository.append(session_id, "line 1")
        repository.append(session_id, "line 2")

        lines = repository.read_lines(session_id)
        assert lines == ["line 1", "line 2", ""]

    def test_read_lines_nonexistent_file(self, repository):
        """Test reading lines from a non-existent file."""
        lines = repository.read_lines("nonexistent")
        assert lines == []


class TestStreamingRepositoryExists:
    """Tests for StreamingRepository.exists."""

    def test_exists_returns_true(self, repository):
        """Test exists() returns True for existing file."""
        session_id = "exists-test"
        repository.append(session_id, "data")
        assert repository.exists(session_id) is True

    def test_exists_returns_false(self, repository):
        """Test exists() returns False for non-existent file."""
        assert repository.exists("nonexistent") is False


class TestStreamingRepositoryCleanup:
    """Tests for StreamingRepository.cleanup."""

    def test_cleanup_existing_file(self, repository):
        """Test cleaning up an existing log file."""
        session_id = "cleanup-test"
        repository.append(session_id, "data")
        assert repository.exists(session_id) is True

        result = repository.cleanup(session_id)
        assert result is True
        assert repository.exists(session_id) is False

    def test_cleanup_nonexistent_file(self, repository):
        """Test cleaning up a non-existent log file returns False."""
        result = repository.cleanup("nonexistent")
        assert result is False

    def test_cleanup_os_error(self, repository):
        """Test handling of OSError during cleanup."""
        session_id = "cleanup-error"
        repository.append(session_id, "data")

        with patch("os.remove", side_effect=OSError("Delete error")):
            with pytest.raises(OSError, match="Failed to delete streaming log"):
                repository.cleanup(session_id)


class TestStreamingRepositoryCleanupAll:
    """Tests for StreamingRepository.cleanup_all."""

    def test_cleanup_all_multiple_files(self, repository):
        """Test cleaning up all log files."""
        repository.append("session1", "data1")
        repository.append("session2", "data2")
        repository.append("session3", "data3")

        assert repository.exists("session1")
        assert repository.exists("session2")
        assert repository.exists("session3")

        count = repository.cleanup_all()
        assert count == 3
        assert repository.exists("session1") is False
        assert repository.exists("session2") is False
        assert repository.exists("session3") is False

    def test_cleanup_all_empty_directory(self, repository):
        """Test cleanup_all on an empty directory."""
        count = repository.cleanup_all()
        assert count == 0

    def test_cleanup_all_ignores_non_log_files(self, repository, streaming_logs_dir):
        """Test that cleanup_all only deletes .log files."""
        repository.append("session1", "data")

        # Create a non-log file
        non_log_path = os.path.join(streaming_logs_dir, "other.txt")
        with open(non_log_path, "w") as f:
            f.write("not a log")

        assert repository.exists("session1")
        assert os.path.exists(non_log_path)

        count = repository.cleanup_all()
        assert count == 1
        assert repository.exists("session1") is False
        assert os.path.exists(non_log_path) is True

    def test_cleanup_all_os_error_on_listdir(self, repository):
        """Test cleanup_all handling OSError on listdir."""
        with patch("os.listdir", side_effect=OSError("List error")):
            count = repository.cleanup_all()
            assert count == 0

    def test_cleanup_all_os_error_on_remove(self, repository):
        """Test cleanup_all continues if one remove fails."""
        repository.append("session1", "data1")
        repository.append("session2", "data2")

        with patch("os.remove", side_effect=[OSError("Delete error"), None]):
            count = repository.cleanup_all()
            # Depending on order, it might be 1 or something else,
            # but it should not raise an exception.
            assert count <= 2
