import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from pipe.core.tools.list_directory import list_directory


class TestListDirectoryTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

        # Patch FileRepositoryFactory.create to use test directory
        self.patcher = patch(
            "pipe.core.tools.list_directory.FileRepositoryFactory.create"
        )
        self.mock_factory = self.patcher.start()

        # Import after patching to get the real repository classes
        from pipe.core.repositories.sandbox_file_repository import SandboxFileRepository

        self.mock_factory.return_value = SandboxFileRepository(self.test_dir)

        # Create dummy files and directories
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f:
            f.write("a")
        with open(os.path.join(self.test_dir, "file2.py"), "w") as f:
            f.write("b")

        self.subdir_path = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.subdir_path)
        with open(os.path.join(self.subdir_path, "file3.txt"), "w") as f:
            f.write("c")

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_list_directory_lists_all(self):
        """
        Tests that the list_directory tool correctly lists all files and subdirectories.
        """
        result = list_directory(path=self.test_dir)

        self.assertIsNotNone(result.data.files)
        self.assertIsNotNone(result.data.directories)
        self.assertIn("file1.txt", result.data.files)
        self.assertIn("file2.py", result.data.files)
        self.assertIn("subdir", result.data.directories)
        self.assertIsNone(result.error)

    def test_list_directory_applies_ignore_patterns(self):
        """
        Tests that the list_directory tool correctly ignores specified patterns.
        """
        result = list_directory(path=self.test_dir, ignore=["*.txt", "subdir"])

        self.assertIsNotNone(result.data.files)
        self.assertIsNotNone(result.data.directories)
        self.assertIn("file2.py", result.data.files)
        self.assertNotIn("file1.txt", result.data.files)
        self.assertNotIn("subdir", result.data.directories)
        self.assertIsNone(result.error)


if __name__ == "__main__":
    unittest.main()
