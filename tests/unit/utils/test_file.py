import json
import os
import tempfile
import unittest
from unittest.mock import patch

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
)


class TestFileUtilities(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_file_lock_and_release(self):
        lock_path = os.path.join(self.test_path, "test.lock")
        with FileLock(lock_path):
            self.assertTrue(os.path.exists(lock_path))
        self.assertFalse(os.path.exists(lock_path))

    @patch("time.sleep", return_value=None)
    def test_file_lock_timeout(self, mock_sleep):
        lock_path = os.path.join(self.test_path, "test.lock")
        # Manually create the lock file to simulate it being held
        open(lock_path, "w").close()
        with self.assertRaises(TimeoutError):
            with FileLock(lock_path):
                pass  # This should not be reached
        os.remove(lock_path)

    def test_locked_json_read_modify_write(self):
        file_path = os.path.join(self.test_path, "data.json")
        lock_path = file_path + ".lock"

        def modifier(data):
            data["key"] = "new_value"
            return data, "return_value"

        result = locked_json_read_modify_write(
            lock_path, file_path, modifier, default_data={"key": "old_value"}
        )
        self.assertEqual(result, "return_value")
        with open(file_path) as f:
            data = json.load(f)
        self.assertEqual(data["key"], "new_value")

    def test_locked_json_read_modify_write_no_default(self):
        file_path = os.path.join(self.test_path, "no_default.json")
        lock_path = file_path + ".lock"
        with self.assertRaises(FileNotFoundError):
            locked_json_read_modify_write(lock_path, file_path, lambda d: d)

    def test_read_yaml_file(self):
        file_path = os.path.join(self.test_path, "config.yml")
        with open(file_path, "w") as f:
            yaml.dump({"key": "value"}, f)
        data = read_yaml_file(file_path)
        self.assertEqual(data, {"key": "value"})
        with self.assertRaises(FileNotFoundError):
            read_yaml_file("nonexistent.yml")

    def test_read_text_file(self):
        file_path = os.path.join(self.test_path, "test.txt")
        with open(file_path, "w") as f:
            f.write("hello")
        self.assertEqual(read_text_file(file_path), "hello")
        self.assertEqual(read_text_file("nonexistent.txt"), "")

    def test_locked_json_write_and_read(self):
        file_path = os.path.join(self.test_path, "data.json")
        lock_path = file_path + ".lock"
        data_to_write = {"a": 1}
        locked_json_write(lock_path, file_path, data_to_write)
        read_data = locked_json_read(lock_path, file_path)
        self.assertEqual(read_data, data_to_write)

    def test_locked_json_read_corrupt(self):
        file_path = os.path.join(self.test_path, "corrupt.json")
        lock_path = file_path + ".lock"
        with open(file_path, "w") as f:
            f.write("{corrupt")
        data = locked_json_read(lock_path, file_path, default_data={"default": True})
        self.assertEqual(data, {"default": True})

    def test_append_to_text_file(self):
        file_path = os.path.join(self.test_path, "append.txt")
        append_to_text_file(file_path, "line1\n")
        append_to_text_file(file_path, "line2")
        with open(file_path) as f:
            self.assertEqual(f.read(), "line1\nline2")

    def test_read_json_file(self):
        file_path = os.path.join(self.test_path, "data.json")
        with open(file_path, "w") as f:
            json.dump({"key": "value"}, f)
        data = read_json_file(file_path)
        self.assertEqual(data, {"key": "value"})
        with self.assertRaises(FileNotFoundError):
            read_json_file("nonexistent.json")
        with open(file_path, "w") as f:
            f.write("{corrupt")
        with self.assertRaises(ValueError):
            read_json_file(file_path)

    def test_create_directory(self):
        dir_path = os.path.join(self.test_path, "new_dir")
        self.assertFalse(os.path.exists(dir_path))
        create_directory(dir_path)
        self.assertTrue(os.path.exists(dir_path))
        create_directory(dir_path)  # Should not raise error

    def test_copy_and_delete_file(self):
        src_path = os.path.join(self.test_path, "src.txt")
        dst_path = os.path.join(self.test_path, "dst.txt")
        with open(src_path, "w") as f:
            f.write("data")

        copy_file(src_path, dst_path)
        self.assertTrue(os.path.exists(dst_path))
        with open(dst_path) as f:
            self.assertEqual(f.read(), "data")

        delete_file(dst_path)
        self.assertFalse(os.path.exists(dst_path))
        delete_file(dst_path)  # Should not raise error


if __name__ == "__main__":
    unittest.main()
