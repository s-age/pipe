import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pipe.core.repositories.process_file_repository import ProcessFileRepository


@pytest.fixture
def processes_dir(tmp_path):
    """Create a temporary directory for process PID files."""
    d = tmp_path / "processes"
    return str(d)


@pytest.fixture
def repository(processes_dir):
    """Create a ProcessFileRepository instance."""
    return ProcessFileRepository(processes_dir)


class TestProcessFileRepositoryInit:
    """Test ProcessFileRepository initialization."""

    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates the processes directory."""
        d = tmp_path / "new_processes"
        assert not d.exists()
        ProcessFileRepository(str(d))
        assert d.exists()
        assert d.is_dir()


class TestProcessFileRepositorySanitize:
    """Test session ID sanitization."""

    def test_sanitize_session_id(self, repository):
        """Test that session IDs are properly sanitized."""
        assert repository._sanitize_session_id("normal-id") == "normal-id"
        assert repository._sanitize_session_id("parent/child") == "parent_child"
        assert repository._sanitize_session_id(r"a\b") == "a_b"
        assert repository._sanitize_session_id("a/b/c") == "a_b_c"


class TestProcessFileRepositoryRead:
    """Test reading PIDs from files."""

    def test_read_pid_success(self, repository, processes_dir):
        """Test reading a valid PID from an existing file."""
        session_id = "test-session"
        pid = 12345
        pid_file = Path(processes_dir) / f"{session_id}.pid"
        pid_file.write_text(str(pid))

        assert repository.read_pid(session_id) == pid

    def test_read_pid_nonexistent(self, repository):
        """Test reading a PID from a non-existent file."""
        assert repository.read_pid("nonexistent") is None

    def test_read_pid_invalid_content(self, repository, processes_dir):
        """Test reading a PID from a file with invalid content."""
        session_id = "invalid-session"
        pid_file = Path(processes_dir) / f"{session_id}.pid"
        pid_file.write_text("not-a-pid")

        assert repository.read_pid(session_id) is None

    def test_read_pid_empty_file(self, repository, processes_dir):
        """Test reading a PID from an empty file."""
        session_id = "empty-session"
        pid_file = Path(processes_dir) / f"{session_id}.pid"
        pid_file.write_text("")

        assert repository.read_pid(session_id) is None

    def test_read_pid_with_subagent_path(self, repository, processes_dir):
        """Test reading a PID with a hierarchical session ID."""
        session_id = "parent/child"
        pid = 999
        # Sanitized filename should be parent_child.pid
        pid_file = Path(processes_dir) / "parent_child.pid"
        pid_file.write_text(str(pid))

        assert repository.read_pid(session_id) == pid


class TestProcessFileRepositoryWrite:
    """Test writing PIDs to files."""

    def test_write_pid_success(self, repository, processes_dir):
        """Test writing a PID to a file."""
        session_id = "write-session"
        pid = 54321
        repository.write_pid(session_id, pid)

        pid_file = Path(processes_dir) / f"{session_id}.pid"
        assert pid_file.exists()
        assert pid_file.read_text() == str(pid)

    def test_write_pid_overwrite(self, repository, processes_dir):
        """Test that write_pid overwrites an existing file."""
        session_id = "overwrite-session"
        repository.write_pid(session_id, 111)
        repository.write_pid(session_id, 222)

        pid_file = Path(processes_dir) / f"{session_id}.pid"
        assert pid_file.read_text() == "222"

    def test_write_pid_atomic_cleanup_on_failure(self, repository):
        """Test that temp files are cleaned up on write failure."""
        session_id = "fail-session"
        pid = 123

        # Simulate failure during rename
        with patch("os.rename", side_effect=OSError("Rename failed")):
            with pytest.raises(OSError, match="Rename failed"):
                repository.write_pid(session_id, pid)

            pid_file_path = repository._get_pid_file_path(session_id)
            temp_path = f"{pid_file_path}.tmp"
            assert not os.path.exists(temp_path)


class TestProcessFileRepositoryDelete:
    """Test deleting PID files."""

    def test_delete_pid_file_success(self, repository, processes_dir):
        """Test deleting an existing PID file."""
        session_id = "delete-session"
        pid_file = Path(processes_dir) / f"{session_id}.pid"
        pid_file.write_text("123")
        assert pid_file.exists()

        repository.delete_pid_file(session_id)
        assert not pid_file.exists()

    def test_delete_pid_file_nonexistent(self, repository):
        """Test deleting a non-existent PID file (should not raise)."""
        repository.delete_pid_file("nonexistent")  # Should not raise

    def test_delete_pid_file_exception_ignored(self, repository, processes_dir):
        """Test that exceptions during deletion are silently ignored."""
        session_id = "error-session"
        pid_file = Path(processes_dir) / f"{session_id}.pid"
        pid_file.write_text("123")

        with patch("os.remove", side_effect=OSError("Deletion failed")):
            # Should not raise
            repository.delete_pid_file(session_id)


class TestProcessFileRepositoryExists:
    """Test checking if PID file exists."""

    def test_exists_true(self, repository, processes_dir):
        """Test exists() returns True for existing file."""
        session_id = "exists-session"
        pid_file = Path(processes_dir) / f"{session_id}.pid"
        pid_file.write_text("123")

        assert repository.exists(session_id) is True

    def test_exists_false(self, repository):
        """Test exists() returns False for non-existent file."""
        assert repository.exists("nonexistent") is False


class TestProcessFileRepositoryList:
    """Test listing all session IDs."""

    def test_list_all_session_ids_empty(self, repository):
        """Test listing when no PID files exist."""
        assert repository.list_all_session_ids() == []

    def test_list_all_session_ids_success(self, repository, processes_dir):
        """Test listing multiple session IDs."""
        sessions = ["session1", "session2", "sub_agent"]
        for s in sessions:
            pid_file = Path(processes_dir) / f"{s}.pid"
            pid_file.write_text("123")

        # Also add a non-pid file to ensure it's ignored
        (Path(processes_dir) / "other.txt").write_text("stuff")

        results = repository.list_all_session_ids()
        assert len(results) == 3
        assert set(results) == set(sessions)

    def test_list_all_session_ids_nonexistent_dir(self, tmp_path):
        """Test listing when the processes directory does not exist."""
        repo = ProcessFileRepository(str(tmp_path / "ghost"))
        # Force remove directory after init
        os.rmdir(str(tmp_path / "ghost"))
        assert repo.list_all_session_ids() == []
