import os
import tempfile
import unittest
from unittest.mock import patch

from pipe.core.tools.replace import replace


class TestReplaceTool(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = self.temp_dir.name
        self.file_path = os.path.join(self.test_path, "test_file.txt")
        with open(self.file_path, "w") as f:
            f.write("Hello world, this is a test.\nHello again!")

        # Patch get_project_root
        self.patcher = patch("pipe.core.tools.replace.get_project_root")
        self.mock_get_project_root = self.patcher.start()
        self.mock_get_project_root.return_value = self.test_path

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def test_replace_success(self):
        result = replace(
            file_path=self.file_path,
            instruction="Replace 'world' with 'Python'",
            old_string="world",
            new_string="Python",
        )
        self.assertEqual(result.data.status, "success")
        self.assertIn("Text replaced successfully", result.data.message)
        self.assertIsNotNone(result.data.diff)

        # Verify file content
        with open(self.file_path) as f:
            content = f.read()
        self.assertEqual(content, "Hello Python, this is a test.\nHello again!")

    def test_old_string_not_found(self):
        result = replace(
            file_path=self.file_path,
            instruction="...",
            old_string="nonexistent",
            new_string="...",
        )
        self.assertIsNone(result.data)
        self.assertIsNotNone(result.error)
        self.assertIn("Old string not found", result.error)

    def test_file_not_found(self):
        result = replace(
            file_path="nonexistent.txt",
            instruction="...",
            old_string="a",
            new_string="b",
        )
        self.assertIsNotNone(result.error)
        self.assertIn("File not found", result.error)

    def test_path_is_directory(self):
        result = replace(
            file_path=self.test_path, instruction="...", old_string="a", new_string="b"
        )
        self.assertIsNotNone(result.error)
        self.assertIn("Path is not a file", result.error)

    def test_path_outside_project_root(self):
        result = replace(
            file_path="/etc/passwd", instruction="...", old_string="a", new_string="b"
        )
        self.assertIsNotNone(result.error)
        # FileSystemRepository.exists returns False for paths outside project root
        self.assertIn("File not found", result.error)

    def test_blocked_path(self):
        # Create a fake .git directory to test protection
        git_dir = os.path.join(self.test_path, ".git")
        os.makedirs(git_dir)
        # We need the file to exist for replace to attempt reading it
        config_path = os.path.join(git_dir, "config")
        with open(config_path, "w") as f:
            f.write("config_a")

        result = replace(
            file_path=config_path,
            instruction="...",
            old_string="a",
            new_string="b",
        )
        self.assertIsNotNone(result.error)
        # FileSystemRepository throws "Access denied: Writing to ... is not allowed"
        # checking for "Access denied" or "not allowed" covers it
        self.assertIn("not allowed", result.error)

    @patch("builtins.open", side_effect=OSError("Test I/O error"))
    def test_general_exception(self, mock_open):
        result = replace(
            file_path=self.file_path, instruction="...", old_string="a", new_string="b"
        )
        self.assertIsNotNone(result.error)
        self.assertIn("Failed to replace text", result.error)


if __name__ == "__main__":
    unittest.main()
