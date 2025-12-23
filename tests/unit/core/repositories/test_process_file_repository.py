import os
from unittest.mock import patch

import pytest
from pipe.core.repositories.process_file_repository import ProcessFileRepository


@pytest.fixture
def processes_dir(tmp_path):
    """Fixture for the processes directory."""
    return str(tmp_path / "processes")


@pytest.fixture
def repository(processes_dir):
    """Fixture for ProcessFileRepository."""
    return ProcessFileRepository(processes_dir=processes_dir)


class TestProcessFileRepositoryInit:
    """Test ProcessFileRepository initialization."""

    def test_init_creates_directory(self, processes_dir):
        """Test that __init__ creates the processes directory."""
        # Directory should be created by fixture's repository initialization
        ProcessFileRepository(processes_dir=processes_dir)
        assert os.path.exists(processes_dir)
        assert os.path.isdir(processes_dir)


class TestProcessFileRepositorySanitize:
    """Test ProcessFileRepository session ID sanitization."""

    def test_sanitize_session_id(self, repository):
        """Test that session IDs are sanitized correctly."""
        assert repository._sanitize_session_id("normal-id") == "normal-id"
        assert repository._sanitize_session_id("parent/child") == "parent_child"
        assert (
            repository._sanitize_session_id(r"path\with\backslashes")
            == "path_with_backslashes"
        )


class TestProcessFileRepositoryReadWrite:
    """Test ProcessFileRepository read and write operations."""

    def test_write_pid_success(self, repository):
        """Test that write_pid creates a PID file with correct content."""
        session_id = "test-session"
        pid = 12345
        repository.write_pid(session_id, pid)

        pid_file_path = repository._get_pid_file_path(session_id)
        assert os.path.exists(pid_file_path)
        with open(pid_file_path, encoding="utf-8") as f:
            assert f.read().strip() == str(pid)

    def test_read_pid_success(self, repository):
        """Test that read_pid reads the correct PID from a file."""
        session_id = "test-session"
        pid = 54321
        repository.write_pid(session_id, pid)

        assert repository.read_pid(session_id) == pid

    def test_read_pid_not_found(self, repository):
        """Test that read_pid returns None if file does not exist."""
        assert repository.read_pid("non-existent") is None

    def test_read_pid_invalid_content(self, repository, processes_dir):
        """Test that read_pid returns None if file content is not a valid integer."""
        session_id = "invalid-pid"
        pid_file_path = repository._get_pid_file_path(session_id)
        with open(pid_file_path, "w", encoding="utf-8") as f:
            f.write("not-a-number")

        assert repository.read_pid(session_id) is None

    def test_read_pid_empty_file(self, repository, processes_dir):
        """Test that read_pid returns None if file is empty."""
        session_id = "empty-pid"
        pid_file_path = repository._get_pid_file_path(session_id)
        with open(pid_file_path, "w", encoding="utf-8") as f:
            f.write("")

        assert repository.read_pid(session_id) is None

    def test_write_pid_atomic_failure_cleanup(self, repository):
        """Test that temp file is removed if write fails before rename."""
        session_id = "fail-session"
        pid = 11111

        with patch("os.rename", side_effect=OSError("Rename failed")):
            with pytest.raises(OSError, match="Rename failed"):
                repository.write_pid(session_id, pid)

        pid_file_path = repository._get_pid_file_path(session_id)
        temp_path = f"{pid_file_path}.tmp"
        assert not os.path.exists(temp_path)
        assert not os.path.exists(pid_file_path)


class TestProcessFileRepositoryDelete:
    """Test ProcessFileRepository delete operations."""

    def test_delete_pid_file_exists(self, repository):
        """Test that delete_pid_file removes an existing PID file."""
        session_id = "delete-me"
        repository.write_pid(session_id, 999)
        assert repository.exists(session_id)

        repository.delete_pid_file(session_id)
        assert not repository.exists(session_id)

    def test_delete_pid_file_not_exists(self, repository):
        """Test that delete_pid_file does not raise error if file does not exist."""
        # Should not raise any exception
        repository.delete_pid_file("never-existed")

    def test_delete_pid_file_permission_error(self, repository):
        """Test that delete_pid_file silently ignores errors during removal."""
        session_id = "permission-error"
        repository.write_pid(session_id, 123)

        with patch("os.remove", side_effect=PermissionError("Permission denied")):
            # Should not raise PermissionError
            repository.delete_pid_file(session_id)
            # File still exists because remove failed
            assert repository.exists(session_id)


class TestProcessFileRepositoryExists:
    """Test ProcessFileRepository existence check."""

    def test_exists_true(self, repository):
        """Test exists returns True when PID file exists."""
        session_id = "exists-test"
        repository.write_pid(session_id, 123)
        assert repository.exists(session_id) is True

    def test_exists_false(self, repository):
        """Test exists returns False when PID file does not exist."""
        assert repository.exists("non-existent") is False


class TestProcessFileRepositoryList:
    """Test ProcessFileRepository list operations."""

    def test_list_all_session_ids(self, repository):
        """Test listing all session IDs with PID files."""
        sessions = ["session1", "session2", "parent/child"]
        for sid in sessions:
            repository.write_pid(sid, 100)

        all_ids = repository.list_all_session_ids()
        assert len(all_ids) == 3
        # Note: list_all_session_ids returns sanitized names as found in filesystem
        assert "session1" in all_ids
        assert "session2" in all_ids
        assert "parent_child" in all_ids

    def test_list_all_session_ids_empty(self, repository):
        """Test listing session IDs when no PID files exist."""
        assert repository.list_all_session_ids() == []

    def test_list_all_session_ids_dir_not_exists(self, processes_dir):
        """Test listing session IDs when the processes directory does not exist."""
        import shutil

        if os.path.exists(processes_dir):
            shutil.rmtree(processes_dir)

        repository = ProcessFileRepository(processes_dir=processes_dir)
        # Manually remove it again to be sure (repository.__init__ creates it)
        shutil.rmtree(processes_dir)

        assert repository.list_all_session_ids() == []
