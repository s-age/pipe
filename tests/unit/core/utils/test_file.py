import json
import os
import time
from unittest.mock import patch

import pytest
import yaml
from pipe.core.utils.file import (
    FileLock,
    append_to_text_file,
    copy_file,
    create_directory,
    delete_file,
    locked_json_read,
    locked_json_read_modify_write,
    locked_json_write,
    read_json_file,
    read_text_file,
    read_yaml_file,
    write_yaml_file,
)


class TestFileLock:
    """Tests for FileLock context manager."""

    def test_file_lock_acquire_and_release(self, tmp_path):
        """Test that FileLock can be acquired and released successfully."""
        lock_path = str(tmp_path / "test.lock")

        assert not os.path.exists(lock_path)
        with FileLock(lock_path):
            assert os.path.exists(lock_path)
        assert not os.path.exists(lock_path)

    def test_file_lock_timeout(self, tmp_path):
        """Test that FileLock raises TimeoutError after timeout."""
        lock_path = str(tmp_path / "test.lock")

        # Manually create the lock file to simulate it being held by another process
        with open(lock_path, "w") as f:
            f.write("locked")

        # Use a short timeout for the test
        with patch("pipe.core.utils.file.time.monotonic") as mock_monotonic:
            # 1. start_time = 0
            # 2. check timeout (0 - 0 < 10)
            # 3. check timeout (11 - 0 >= 10) -> raise TimeoutError
            mock_monotonic.side_effect = [0, 0.05, 11]
            with patch("pipe.core.utils.file.time.sleep") as mock_sleep:
                with pytest.raises(TimeoutError, match="Could not acquire lock"):
                    with FileLock(lock_path):
                        pass
                # Verify sleep was called (line 47)
                mock_sleep.assert_called()

    def test_file_lock_stale_lock_removal_failure(self, tmp_path):
        """Test FileLock handles OSError when removing stale lock."""
        lock_path = str(tmp_path / "test.lock")

        # Create a stale lock file
        with open(lock_path, "w") as f:
            f.write("stale")
        stale_time = time.time() - 400
        os.utime(lock_path, (stale_time, stale_time))

        # Mock os.remove to raise OSError once
        with patch("pipe.core.utils.file.os.remove") as mock_remove:
            mock_remove.side_effect = [OSError("Permission denied"), None]
            # It will retry acquiring the lock.
            # We need os.open to fail once then succeed.
            with patch("pipe.core.utils.file.os.open") as mock_open:
                # 1. FileExistsError (stale check)
                # 2. Success
                mock_open.side_effect = [FileExistsError(), 1]
                with patch("pipe.core.utils.file.os.close"):
                    with FileLock(lock_path):
                        pass
            # Verify os.remove was called for stale lock
            assert mock_remove.call_count >= 1

    def test_file_lock_getmtime_failure(self, tmp_path):
        """Test FileLock handles OSError when getmtime fails."""
        lock_path = str(tmp_path / "test.lock")

        with patch("pipe.core.utils.file.os.path.getmtime") as mock_getmtime:
            mock_getmtime.side_effect = OSError("File disappeared")
            with patch("pipe.core.utils.file.os.open") as mock_open:
                # 1. FileExistsError (stale check -> OSError)
                # 2. Success
                mock_open.side_effect = [FileExistsError(), 1]
                with patch("pipe.core.utils.file.os.close"):
                    with FileLock(lock_path):
                        pass

    def test_file_lock_release_failure(self, tmp_path):
        """Test FileLock handles OSError when releasing lock fails."""
        lock_path = str(tmp_path / "test.lock")

        with patch("pipe.core.utils.file.os.remove") as mock_remove:
            mock_remove.side_effect = OSError("Already removed")
            with FileLock(lock_path):
                pass
            # Should not raise exception

    def test_file_lock_stale_lock_removal_hits_print(self, tmp_path, capsys):
        """Test that FileLock prints a warning when removing a stale lock."""
        lock_path = str(tmp_path / "stale_print.lock")

        # Create a stale lock file
        with open(lock_path, "w") as f:
            f.write("stale")
        stale_time = time.time() - 400
        os.utime(lock_path, (stale_time, stale_time))

        with FileLock(lock_path):
            pass

        captured = capsys.readouterr()
        assert "WARNING: Removed stale lock file" in captured.out
        # Should be around 400s
        assert "age: 400" in captured.out or "age: 40" in captured.out

    def test_file_lock_removes_lock_on_exception(self, tmp_path):
        """Test that FileLock removes the lock file even if an exception occurs."""
        lock_path = str(tmp_path / "test.lock")

        try:
            with FileLock(lock_path):
                raise ValueError("Test error")
        except ValueError:
            pass

        assert not os.path.exists(lock_path)


class TestLockedJsonReadModifyWrite:
    """Tests for locked_json_read_modify_write function."""

    def test_read_modify_write_success(self, tmp_path):
        """Test successful read-modify-write operation."""
        file_path = str(tmp_path / "test.json")
        lock_path = str(tmp_path / "test.lock")
        initial_data = {"count": 1}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)

        def modifier(data):
            data["count"] += 1
            return data

        locked_json_read_modify_write(lock_path, file_path, modifier)

        with open(file_path, encoding="utf-8") as f:
            result = json.load(f)
        assert result["count"] == 2

    def test_read_modify_write_with_return_value(self, tmp_path):
        """Test read-modify-write operation that returns a value."""
        file_path = str(tmp_path / "test.json")
        lock_path = str(tmp_path / "test.lock")
        initial_data = {"items": [1]}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)

        def modifier(data):
            data["items"].append(2)
            return data, "success_flag"

        return_val = locked_json_read_modify_write(lock_path, file_path, modifier)

        assert return_val == "success_flag"
        with open(file_path, encoding="utf-8") as f:
            result = json.load(f)
        assert result["items"] == [1, 2]

    def test_read_modify_write_in_place(self, tmp_path):
        """Test read-modify-write with in-place modification (returning None)."""
        file_path = str(tmp_path / "test.json")
        lock_path = str(tmp_path / "test.lock")
        initial_data = {"count": 1}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)

        def modifier(data):
            data["count"] = 10
            return None

        locked_json_read_modify_write(lock_path, file_path, modifier)

        with open(file_path, encoding="utf-8") as f:
            result = json.load(f)
        assert result["count"] == 10

    def test_read_modify_write_default_data(self, tmp_path):
        """Test read-modify-write when file doesn't exist, using default data."""
        file_path = str(tmp_path / "nonexistent.json")
        lock_path = str(tmp_path / "test.lock")
        default_data = {"count": 0}

        def modifier(data):
            data["count"] += 1
            return data

        locked_json_read_modify_write(
            lock_path, file_path, modifier, default_data=default_data
        )

        with open(file_path, encoding="utf-8") as f:
            result = json.load(f)
        assert result["count"] == 1

    def test_read_modify_write_corrupt_json(self, tmp_path):
        """Test read-modify-write handles corrupted JSON by using default data."""
        file_path = str(tmp_path / "corrupt.json")
        lock_path = str(tmp_path / "test.lock")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        default_data = {"count": 100}

        def modifier(data):
            data["count"] += 1
            return data

        locked_json_read_modify_write(
            lock_path, file_path, modifier, default_data=default_data
        )

        with open(file_path, encoding="utf-8") as f:
            result = json.load(f)
        assert result["count"] == 101

    def test_read_modify_write_file_not_found_no_default(self, tmp_path):
        """Test that read-modify-write raises FileNotFoundError if no default data."""
        file_path = str(tmp_path / "nonexistent.json")
        lock_path = str(tmp_path / "test.lock")

        with pytest.raises(FileNotFoundError):
            locked_json_read_modify_write(lock_path, file_path, lambda x: x)


class TestYamlOperations:
    """Tests for YAML read/write operations."""

    def test_read_yaml_file_success(self, tmp_path):
        """Test reading a valid YAML file."""
        file_path = str(tmp_path / "test.yaml")
        data = {"key": "value", "list": [1, 2, 3]}
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

        result = read_yaml_file(file_path)
        assert result == data

    def test_read_yaml_file_not_found(self, tmp_path):
        """Test reading a non-existent YAML file raises FileNotFoundError."""
        file_path = str(tmp_path / "nonexistent.yaml")
        with pytest.raises(FileNotFoundError):
            read_yaml_file(file_path)

    def test_write_yaml_file(self, tmp_path):
        """Test writing data to a YAML file."""
        file_path = str(tmp_path / "output.yaml")
        data = {"a": 1, "b": {"c": 2}}

        write_yaml_file(file_path, data)

        assert os.path.exists(file_path)
        with open(file_path, encoding="utf-8") as f:
            result = yaml.safe_load(f)
        assert result == data


class TestTextOperations:
    """Tests for text file operations."""

    def test_read_text_file_success(self, tmp_path):
        """Test reading an existing text file."""
        file_path = str(tmp_path / "test.txt")
        content = "Hello\nWorld"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        assert read_text_file(file_path) == content

    def test_read_text_file_not_found(self, tmp_path):
        """Test reading a non-existent text file returns empty string."""
        file_path = str(tmp_path / "nonexistent.txt")
        assert read_text_file(file_path) == ""

    def test_append_to_text_file(self, tmp_path):
        """Test appending content to a text file."""
        file_path = str(tmp_path / "append.txt")
        initial = "First line\n"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(initial)

        append_to_text_file(file_path, "Second line")

        with open(file_path, encoding="utf-8") as f:
            result = f.read()
        assert result == initial + "Second line"


class TestLockedJsonReadWrite:
    """Tests for locked_json_read and locked_json_write functions."""

    def test_locked_json_write(self, tmp_path):
        """Test safely writing JSON under lock."""
        file_path = str(tmp_path / "locked.json")
        lock_path = str(tmp_path / "locked.lock")
        data = {"id": 123, "name": "test"}

        locked_json_write(lock_path, file_path, data)

        with open(file_path, encoding="utf-8") as f:
            result = json.load(f)
        assert result == data

    def test_locked_json_read_success(self, tmp_path):
        """Test safely reading JSON under lock."""
        file_path = str(tmp_path / "locked.json")
        lock_path = str(tmp_path / "locked.lock")
        data = {"status": "ok"}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        result = locked_json_read(lock_path, file_path)
        assert result == data

    def test_locked_json_read_not_found(self, tmp_path):
        """Test locked_json_read returns default_data if file is missing."""
        file_path = str(tmp_path / "missing.json")
        lock_path = str(tmp_path / "locked.lock")
        default = {"default": True}

        result = locked_json_read(lock_path, file_path, default_data=default)
        assert result == default

    def test_locked_json_read_invalid_json(self, tmp_path):
        """Test locked_json_read returns default_data if JSON is invalid."""
        file_path = str(tmp_path / "invalid.json")
        lock_path = str(tmp_path / "locked.lock")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("{ invalid }")

        result = locked_json_read(lock_path, file_path, default_data="fallback")
        assert result == "fallback"

    def test_locked_json_read_empty_file(self, tmp_path):
        """Test locked_json_read returns default_data if file is empty."""
        file_path = str(tmp_path / "empty.json")
        lock_path = str(tmp_path / "locked.lock")
        with open(file_path, "w", encoding="utf-8"):
            pass

        result = locked_json_read(lock_path, file_path, default_data="empty")
        assert result == "empty"


class TestReadJsonFile:
    """Tests for read_json_file function."""

    def test_read_json_file_success(self, tmp_path):
        """Test reading a valid JSON file."""
        file_path = str(tmp_path / "test.json")
        data = {"foo": "bar"}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        assert read_json_file(file_path) == data

    def test_read_json_file_not_found(self, tmp_path):
        """Test reading non-existent JSON file raises FileNotFoundError."""
        file_path = str(tmp_path / "nonexistent.json")
        with pytest.raises(FileNotFoundError):
            read_json_file(file_path)

    def test_read_json_file_invalid(self, tmp_path):
        """Test reading invalid JSON file raises ValueError."""
        file_path = str(tmp_path / "invalid.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("{ bad json }")

        with pytest.raises(ValueError, match="Invalid JSON"):
            read_json_file(file_path)


class TestFileSystemOperations:
    """Tests for general file system operations."""

    def test_create_directory(self, tmp_path):
        """Test creating a directory."""
        dir_path = str(tmp_path / "new_dir" / "sub_dir")
        create_directory(dir_path)
        assert os.path.isdir(dir_path)

        # Should not raise error if already exists
        create_directory(dir_path)
        assert os.path.isdir(dir_path)

    def test_copy_file(self, tmp_path):
        """Test copying a file."""
        src = str(tmp_path / "src.txt")
        dst = str(tmp_path / "dst.txt")
        content = "source content"
        with open(src, "w", encoding="utf-8") as f:
            f.write(content)

        copy_file(src, dst)

        assert os.path.exists(dst)
        with open(dst, encoding="utf-8") as f:
            assert f.read() == content

    def test_delete_file(self, tmp_path):
        """Test deleting a file."""
        file_path = str(tmp_path / "delete_me.txt")
        with open(file_path, "w") as f:
            f.write("data")

        assert os.path.exists(file_path)
        delete_file(file_path)
        assert not os.path.exists(file_path)

        # Should not raise error if file doesn't exist
        delete_file(file_path)
        assert not os.path.exists(file_path)
