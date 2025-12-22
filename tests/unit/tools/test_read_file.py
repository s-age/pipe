import json
import os
import shutil
import tempfile
import unittest
import warnings
from unittest.mock import patch

from pipe.core.tools.read_file import read_file

from tests.factories.models.settings_factory import create_test_settings


class TestReadFile(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

        self.test_dir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.test_dir, "sessions")
        os.makedirs(self.sessions_dir)
        self.session_id = "test_read_file_session"
        self.session_file = os.path.join(self.sessions_dir, f"{self.session_id}.json")

        # Create a dummy session file
        self.initial_session_data = {
            "session_id": self.session_id,
            "turns": [],
            "references": [],
            "created_at": "2023-01-01T00:00:00",
            "purpose": "test",
        }
        with open(self.session_file, "w") as f:
            json.dump(self.initial_session_data, f)

        # Create a dummy file to read
        self.dummy_file_path = os.path.join(self.test_dir, "dummy.txt")
        with open(self.dummy_file_path, "w") as f:
            f.write("dummy content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    @patch("pipe.core.tools.read_file.get_project_root")
    def test_read_file_success(self, mock_get_project_root, mock_get_settings):
        # Mock get_project_root to return the test dir
        mock_get_project_root.return_value = self.test_dir

        # Mock settings to point to our temp sessions dir
        mock_settings = create_test_settings(
            sessions_path=self.sessions_dir,
            model_name="gemini-2.0-flash-exp",
        )
        mock_get_settings.return_value = mock_settings

        # Set environment variable
        os.environ["PIPE_SESSION_ID"] = self.session_id

        result = read_file(absolute_path=self.dummy_file_path)

        if result.error:
            self.fail(f"read_file returned error: {result.error}")

        self.assertIsNotNone(result.data.message)
        self.assertIn("added or updated", result.data.message)

        # Verify the session file
        with open(self.session_file) as f:
            session_data = json.load(f)

        self.assertEqual(len(session_data["references"]), 1)
        ref = session_data["references"][0]
        # Normalize paths for comparison
        expected_path = os.path.normpath(os.path.abspath(self.dummy_file_path))
        self.assertEqual(os.path.normpath(ref["path"]), expected_path)
        self.assertEqual(ref["ttl"], 3)

    @patch("pipe.core.tools.read_file.get_project_root")
    def test_read_file_no_session(self, mock_get_project_root):
        mock_get_project_root.return_value = self.test_dir
        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

        result = read_file(absolute_path=self.dummy_file_path)
        if result.error:
            self.fail(f"read_file returned error: {result.error}")
        self.assertIsNotNone(result.data.content)
        self.assertEqual(result.data.content, "dummy content")
        self.assertIsNone(result.error)

        @patch("pipe.core.tools.read_file.get_project_root")
        def test_read_file_not_found(self, mock_get_project_root):
            mock_get_project_root.return_value = self.test_dir

            os.environ["PIPE_SESSION_ID"] = self.session_id

            result = read_file(
                absolute_path=os.path.join(self.test_dir, "non_existent_file.txt")
            )

            self.assertIsNotNone(result.error)

            self.assertIn("File not found", result.error)
