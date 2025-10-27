import os
import shutil
import tempfile
import unittest

from pipe.core.tools.list_directory import list_directory


class TestListDirectoryTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

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
        shutil.rmtree(self.test_dir)

    def test_list_directory_lists_all(self):
        """
        Tests that the list_directory tool correctly lists all files and subdirectories.
        """
        result = list_directory(path=self.test_dir)

        self.assertIn("files", result)
        self.assertIn("directories", result)
        self.assertNotIn("error", result)

        self.assertIn("file1.txt", result["files"])
        self.assertIn("file2.py", result["files"])
        self.assertIn("subdir", result["directories"])

    def test_list_directory_applies_ignore_patterns(self):
        """
        Tests that the list_directory tool correctly ignores specified patterns.
        """
        result = list_directory(path=self.test_dir, ignore=["*.txt", "subdir"])

        self.assertIn("files", result)
        self.assertIn("directories", result)
        self.assertNotIn("error", result)

        self.assertNotIn("file1.txt", result["files"])
        self.assertIn("file2.py", result["files"])
        self.assertNotIn("subdir", result["directories"])


if __name__ == "__main__":
    unittest.main()
