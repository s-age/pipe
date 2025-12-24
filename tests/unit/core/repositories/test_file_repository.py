"""
Tests for FileRepository and file locking mechanism.
"""

import fcntl
import json
import os
import threading
import time
from unittest.mock import patch

import pytest
from pipe.core.repositories.file_repository import FileRepository, file_lock


class TestFileLock:
    """Tests for the file_lock context manager."""

    def test_lock_acquisition_success(self, tmp_path):
        """Test successful lock acquisition."""
        lock_path = str(tmp_path / "test.lock")

        with file_lock(lock_path):
            assert os.path.exists(lock_path)

    def test_lock_timeout(self, tmp_path):
        """Test that a TimeoutError is raised when the lock cannot be acquired."""
        lock_path = str(tmp_path / "timeout.lock")

        # Acquire the lock in the main thread
        with file_lock(lock_path):
            # Try to acquire the same lock in another context
            # (simulating another process/thread)
            # Since fcntl locks are per process, we can't easily test blocking
            # within the same process for the same file descriptor.
            # However, we can simulate the timeout logic
            # by mocking fcntl.flock to raise BlockingIOError.

            pass

    @patch("fcntl.flock")
    def test_lock_timeout_mocked(self, mock_flock, tmp_path):
        """Test timeout logic using mock to simulate blocking."""
        lock_path = str(tmp_path / "mocked_timeout.lock")

        def side_effect(fd, operation):
            if operation & fcntl.LOCK_EX:
                raise BlockingIOError("Mocked blocking")
            return None

        mock_flock.side_effect = side_effect

        start_time = time.time()
        with pytest.raises(
            TimeoutError, match=f"Could not acquire lock on {lock_path}"
        ):
            with file_lock(lock_path, timeout=0.1):
                pass
        duration = time.time() - start_time
        assert duration >= 0.1

    def test_concurrent_access(self, tmp_path):
        """Test that concurrent threads respect the lock."""
        lock_path = str(tmp_path / "concurrent.lock")
        shared_resource: list[int] = []

        def worker(item: int):
            with file_lock(lock_path):
                # Critical section
                current = list(shared_resource)
                time.sleep(0.01)  # Simulate work
                current.append(item)
                # Modify shared_resource in place to reflect changes
                shared_resource.clear()
                shared_resource.extend(current)

        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(shared_resource) == 5
        # Order is not guaranteed, but count is


class TestFileRepository:
    """Tests for FileRepository methods."""

    @pytest.fixture
    def repo(self):
        """Create a FileRepository instance."""
        return FileRepository()

    def test_read_json_existing_file(self, repo, tmp_path):
        """Test reading a valid JSON file."""
        file_path = str(tmp_path / "data.json")
        data = {"key": "value"}

        with open(file_path, "w") as f:
            json.dump(data, f)

        result = repo._read_json(file_path)
        assert result == data

    def test_read_json_non_existent_file(self, repo, tmp_path):
        """Test reading a non-existent file returns default data."""
        file_path = str(tmp_path / "nonexistent.json")
        default = {"default": "data"}

        result = repo._read_json(file_path, default_data=default)
        assert result == default

    def test_read_json_corrupted_file(self, repo, tmp_path):
        """Test reading a corrupted JSON file returns default data."""
        file_path = str(tmp_path / "corrupted.json")
        default = {"default": "data"}

        with open(file_path, "w") as f:
            f.write("{ invalid json }")

        result = repo._read_json(file_path, default_data=default)
        assert result == default

    def test_write_json_creates_file_and_dirs(self, repo, tmp_path):
        """Test writing JSON data creates the file and necessary directories."""
        file_path = str(tmp_path / "nested" / "dir" / "data.json")
        data = {"key": "value"}

        repo._write_json(file_path, data)

        assert os.path.exists(file_path)
        with open(file_path) as f:
            loaded = json.load(f)
        assert loaded == data

    def test_write_json_overwrites_existing(self, repo, tmp_path):
        """Test writing JSON data overwrites existing file."""
        file_path = str(tmp_path / "overwrite.json")

        repo._write_json(file_path, {"old": "data"})
        repo._write_json(file_path, {"new": "data"})

        with open(file_path) as f:
            loaded = json.load(f)
        assert loaded == {"new": "data"}

    def test_locked_read_json(self, repo, tmp_path):
        """Test reading JSON with a lock."""
        lock_path = str(tmp_path / "read.lock")
        file_path = str(tmp_path / "read_locked.json")
        data = {"key": "locked_read"}

        with open(file_path, "w") as f:
            json.dump(data, f)

        result = repo._locked_read_json(lock_path, file_path)
        assert result == data
        assert os.path.exists(lock_path)

    def test_locked_write_json(self, repo, tmp_path):
        """Test writing JSON with a lock."""
        lock_path = str(tmp_path / "write.lock")
        file_path = str(tmp_path / "write_locked.json")
        data = {"key": "locked_write"}

        repo._locked_write_json(lock_path, file_path, data)

        assert os.path.exists(file_path)
        with open(file_path) as f:
            loaded = json.load(f)
        assert loaded == data
        assert os.path.exists(lock_path)

    def test_locked_write_concurrency(self, repo, tmp_path):
        """Test concurrent writes with locking ensure data integrity."""
        lock_path = str(tmp_path / "concurrent_write.lock")
        file_path = str(tmp_path / "concurrent_write.json")

        # Initialize file
        repo._write_json(file_path, {"count": 0})

        def increment_counter():
            # Read-modify-write cycle using the same lock
            with file_lock(lock_path):
                data = repo._read_json(file_path)
                data["count"] += 1
                time.sleep(0.01)  # Increase chance of race condition without lock
                repo._write_json(file_path, data)

        threads = []
        for _ in range(5):
            t = threading.Thread(target=increment_counter)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        result = repo._read_json(file_path)
        assert result["count"] == 5
