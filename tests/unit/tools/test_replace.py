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

        # Patch os.getcwd to return the temp dir, simulating it as the project root
        self.getcwd_patcher = patch("os.getcwd", return_value=self.test_path)
        self.mock_getcwd = self.getcwd_patcher.start()

    def tearDown(self):
        self.getcwd_patcher.stop()
        self.temp_dir.cleanup()

    def test_replace_success(self):
        result = replace(
            file_path=self.file_path,
            instruction="Replace 'world' with 'Python'",
            old_string="world",
            new_string="Python",
        )
        self.assertEqual(result["status"], "success")
        self.assertIn("Text replaced successfully", result["message"])
        self.assertIn("diff", result["message"])
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
        self.assertEqual(result["status"], "failed")
        self.assertIn("Old string not found", result["message"])

    def test_file_not_found(self):
        result = replace(
            file_path="nonexistent.txt",
            instruction="...",
            old_string="a",
            new_string="b",
        )
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])

    def test_path_is_directory(self):
        result = replace(
            file_path=self.test_path, instruction="...", old_string="a", new_string="b"
        )
        self.assertIn("error", result)
        self.assertIn("Path is not a file", result["error"])

    def test_path_outside_project_root(self):
        result = replace(
            file_path="/etc/passwd", instruction="...", old_string="a", new_string="b"
        )
        self.assertIn("error", result)
        self.assertIn("Modifying files outside project root", result["error"])

    def test_blocked_path(self):
        # Create a fake .git directory to test protection
        git_dir = os.path.join(self.test_path, ".git")
        os.makedirs(git_dir)
        result = replace(
            file_path=os.path.join(git_dir, "config"),
            instruction="...",
            old_string="a",
            new_string="b",
        )
        self.assertIn("error", result)
        self.assertIn("sensitive path", result["error"])

    @patch("builtins.open", side_effect=OSError("Test I/O error"))
    def test_general_exception(self, mock_open):
        result = replace(
            file_path=self.file_path, instruction="...", old_string="a", new_string="b"
        )
        self.assertIn("error", result)
        self.assertIn("Failed to replace text", result["error"])


if __name__ == "__main__":
    unittest.main()
