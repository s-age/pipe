import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.tools.read_many_files import read_many_files


class TestReadManyFilesTool(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = self.temp_dir.name

        # Create a nested structure
        self.dir1 = os.path.join(self.test_path, "dir1")
        self.git_dir = os.path.join(self.test_path, ".git")
        os.makedirs(self.dir1)
        os.makedirs(self.git_dir)

        self.file1 = os.path.join(self.dir1, "file1.txt")
        self.file2 = os.path.join(self.dir1, "file2.log")
        self.ignored_file = os.path.join(self.git_dir, "config")

        with open(self.file1, "w") as f:
            f.write("file1")
        with open(self.file2, "w") as f:
            f.write("file2")
        with open(self.ignored_file, "w") as f:
            f.write("ignored")

        self.mock_session_service = MagicMock()
        self.session_id = "test_session"

        self.getcwd_patcher = patch("os.getcwd", return_value=self.test_path)
        self.mock_getcwd = self.getcwd_patcher.start()

    def tearDown(self):
        self.getcwd_patcher.stop()
        self.temp_dir.cleanup()

    def test_no_session_service(self):
        result = read_many_files(paths=["*"])
        self.assertIn("error", result)

    def test_simple_glob(self):
        read_many_files(
            paths=["dir1/*.txt"],
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.mock_session_service.add_references.assert_called_once_with(
            self.session_id, [os.path.abspath(self.file1)]
        )

    def test_directory_glob(self):
        read_many_files(
            paths=["dir1"],
            useDefaultExcludes=False,  # Disable default excludes to find .log file
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.mock_session_service.add_references.assert_called_once()
        called_args = self.mock_session_service.add_references.call_args[0][1]
        self.assertIn(os.path.abspath(self.file1), called_args)
        self.assertIn(os.path.abspath(self.file2), called_args)

    def test_default_excludes(self):
        read_many_files(
            paths=["**/*"],
            useDefaultExcludes=True,
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.mock_session_service.add_references.assert_called_once()
        called_args = self.mock_session_service.add_references.call_args[0][1]
        self.assertNotIn(os.path.abspath(self.ignored_file), called_args)

    def test_custom_exclude(self):
        read_many_files(
            paths=["dir1/*"],
            exclude=["*.log"],
            useDefaultExcludes=False,
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.mock_session_service.add_references.assert_called_once_with(
            self.session_id, [os.path.abspath(self.file1)]
        )

    def test_custom_include(self):
        read_many_files(
            paths=["dir1/*"],
            include=["*.log"],
            useDefaultExcludes=False,  # Disable default excludes
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.mock_session_service.add_references.assert_called_once_with(
            self.session_id, [os.path.abspath(self.file2)]
        )

    def test_no_files_found(self):
        result = read_many_files(
            paths=["*.nonexistent"],
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.assertEqual(result, {"message": "No files found matching the criteria."})

    @patch(
        "pipe.core.tools.read_many_files.std_glob.glob",
        side_effect=Exception("Test error"),
    )
    def test_general_exception(self, mock_glob):
        result = read_many_files(
            paths=["*"],
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
