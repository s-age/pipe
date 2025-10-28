import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from pipe.core.tools.glob import glob


class TestGlobTool(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = self.temp_dir.name

        # Create some files for testing
        self.file1 = os.path.join(self.test_path, "file1.txt")
        self.file2 = os.path.join(self.test_path, "file2.log")
        self.ignored_file = os.path.join(self.test_path, "ignored.txt")

        with open(self.file1, "w") as f:
            f.write("file1")
        with open(self.file2, "w") as f:
            f.write("file2")
        with open(self.ignored_file, "w") as f:
            f.write("ignored")

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("subprocess.run")
    def test_glob_simple_pattern(self, mock_subprocess_run):
        # Mock git to return no ignored files
        mock_subprocess_run.return_value.stdout = ""

        result = glob(pattern="*.txt", path=self.test_path)

        self.assertIn("content", result)
        content = result["content"].split("\n")

        self.assertIn(self.file1, content)
        self.assertIn(self.ignored_file, content)
        self.assertNotIn(self.file2, content)

    @patch("subprocess.run")
    def test_glob_with_gitignore(self, mock_subprocess_run):
        # Mock git to return the ignored file
        mock_subprocess_run.return_value.stdout = "ignored.txt\n"

        result = glob(pattern="*.txt", path=self.test_path)

        self.assertIn("content", result)
        content = result["content"]

        self.assertIn(self.file1, content)
        self.assertNotIn("ignored.txt", content)

    @patch("subprocess.run")
    def test_glob_git_command_fails(self, mock_subprocess_run):
        # Mock git command failing
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "git")

        result = glob(pattern="*.txt", path=self.test_path)

        self.assertIn("content", result)
        content = result["content"].split("\n")

        # Should return all files as if git wasn't there
        self.assertIn(self.file1, content)
        self.assertIn(self.ignored_file, content)

    @patch("subprocess.run", side_effect=Exception("Test subprocess error"))
    def test_glob_general_exception(self, mock_subprocess_run):
        """Tests that a general exception is caught and an error message is returned."""
        result = glob(pattern="*")
        self.assertIn("content", result)
        self.assertIn(
            "Error inside glob tool: Test subprocess error", result["content"]
        )


if __name__ == "__main__":
    unittest.main()
