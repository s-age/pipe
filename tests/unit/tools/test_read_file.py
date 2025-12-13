import json
import os
import shutil
import tempfile
import unittest
import warnings
from unittest.mock import patch

from pipe.core.tools.read_file import read_file


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
    @patch("pipe.core.tools.read_file.os.getcwd")
    def test_read_file_success(self, mock_getcwd, mock_get_settings):
        # Mock os.getcwd to return the test dir
        mock_getcwd.return_value = self.test_dir

        # Mock settings to point to our temp sessions dir
        from pipe.core.models.settings import Settings

        mock_settings = Settings(
            sessions_path=self.sessions_dir,
            parameters={
                "temperature": {"value": 0.5, "description": "d"},
                "top_p": {"value": 0.5, "description": "d"},
                "top_k": {"value": 40, "description": "d"},
            },
            model="gemini-2.0-flash-exp",
        )
        mock_get_settings.return_value = mock_settings

        # Set environment variable
        os.environ["PIPE_SESSION_ID"] = self.session_id

        result = read_file(absolute_path=self.dummy_file_path)

        if "error" in result:
            self.fail(f"read_file returned error: {result['error']}")

        self.assertIn("message", result)
        self.assertIn("added or updated", result["message"])

        # Verify the session file
        with open(self.session_file) as f:
            session_data = json.load(f)

        self.assertEqual(len(session_data["references"]), 1)
        ref = session_data["references"][0]
        # Normalize paths for comparison
        expected_path = os.path.normpath(os.path.abspath(self.dummy_file_path))
        self.assertEqual(os.path.normpath(ref["path"]), expected_path)
        self.assertEqual(ref["ttl"], 3)

    def test_read_file_no_session(self):
        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

        result = read_file(absolute_path=self.dummy_file_path)
        self.assertIn("content", result)
        self.assertEqual(result["content"], "dummy content")
        self.assertNotIn("error", result)

    def test_read_file_not_found(self):
        os.environ["PIPE_SESSION_ID"] = self.session_id
        result = read_file(absolute_path="non_existent_file.txt")
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])
