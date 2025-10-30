import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, Mock

from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_service import SessionService
from pipe.core.tools.read_many_files import read_many_files


class TestReadManyFilesTool(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        self.session_id = "test_session"

        # Create dummy files and directories for testing
        self.dir1 = os.path.join(self.project_root, "dir1")
        os.makedirs(self.dir1)
        self.file1 = os.path.join(self.dir1, "file1.txt")
        with open(self.file1, "w") as f:
            f.write("content1")
        self.file2 = os.path.join(self.dir1, "file2.log")
        with open(self.file2, "w") as f:
            f.write("content2")
        self.file3 = os.path.join(self.project_root, "file3.md")
        with open(self.file3, "w") as f:
            f.write("content3")

        settings_data = {
            "model": "test-model",
            "search_model": "test-model",
            "context_limit": 10000,
            "api_mode": "gemini-api",
            "language": "en",
            "yolo": False,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)
        self.mock_repository = Mock(spec=SessionRepository)
        self.mock_session_service = MagicMock(spec=SessionService)
        self.mock_session_service.project_root = self.project_root

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_simple_glob(self):
        read_many_files(
            paths=["dir1/*.txt"],
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.mock_session_service.add_multiple_references.assert_called_once_with(
            self.session_id, [os.path.abspath(self.file1)]
        )

    def test_directory_glob(self):
        read_many_files(
            paths=["dir1"],
            useDefaultExcludes=False,  # Disable default excludes to find .log file
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        expected_files = sorted(
            [os.path.abspath(self.file1), os.path.abspath(self.file2)]
        )
        self.mock_session_service.add_multiple_references.assert_called_once_with(
            self.session_id, expected_files
        )

    def test_default_excludes(self):
        read_many_files(
            paths=["**/*"],
            useDefaultExcludes=True,
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        # Only file1.txt and file3.md should be included, file2.log is excluded
        # by default
        expected_files = sorted(
            [os.path.abspath(self.file1), os.path.abspath(self.file3)]
        )
        self.mock_session_service.add_multiple_references.assert_called_once_with(
            self.session_id, expected_files
        )

    def test_custom_exclude(self):
        read_many_files(
            paths=["dir1/*"],
            exclude=["*.log"],
            useDefaultExcludes=False,
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.mock_session_service.add_multiple_references.assert_called_once_with(
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
        self.mock_session_service.add_multiple_references.assert_called_once_with(
            self.session_id, [os.path.abspath(self.file2)]
        )

    def test_no_files_found(self):
        result = read_many_files(
            paths=["non_existent_dir/*"],
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.assertIn("message", result)
        self.assertEqual(result["message"], "No files found matching the criteria.")
        self.mock_session_service.add_multiple_references.assert_not_called()

    def test_no_session_service(self):
        result = read_many_files(paths=["dir1/*.txt"], session_id=self.session_id)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "This tool requires an active session.")

    def test_error_handling(self):
        self.mock_session_service.add_multiple_references.side_effect = Exception(
            "Test error"
        )
        result = read_many_files(
            paths=["dir1/*.txt"],
            session_service=self.mock_session_service,
            session_id=self.session_id,
        )
        self.assertIn("error", result)
        self.assertIn("Test error", result["error"])


if __name__ == "__main__":
    unittest.main()
