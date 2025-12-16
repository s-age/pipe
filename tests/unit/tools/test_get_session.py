import json
import os
import shutil
import unittest
import warnings
from unittest.mock import patch

from pipe.core.tools.get_session import get_session


class TestGetSession(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

        self.test_session_id = "get_session_test"
        self.tmp_dir = "/tmp/pipe_tests/sessions_get"
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.session_file = os.path.join(self.tmp_dir, f"{self.test_session_id}.json")

        # Create a dummy session file
        session_data = {
            "session_id": self.test_session_id,
            "turns": [
                {"type": "user_task", "instruction": "Hello", "files": []},
                {"type": "model_response", "content": "Hi there!", "files": []},
            ],
            "created_at": "2023-01-01T00:00:00",
            "purpose": "Test",
            "background": "Test background",
            "roles": [],
            "multi_step_reasoning_enabled": False,
            "token_count": 0,
            "hyperparameters": {
                "temperature": 0.5,
                "top_p": 0.9,
                "top_k": 40,
            },
            "artifacts": [],
        }
        with open(self.session_file, "w") as f:
            json.dump(session_data, f)

        # Mock settings dictionary
        self.mock_settings = {
            "api_key": "dummy",
            "timezone": "UTC",
            "language": "en",
            "sessions_path": self.tmp_dir,
            "parameters": {
                "temperature": {"value": 0.5, "description": "Temp"},
                "top_p": {"value": 0.9, "description": "Top P"},
                "top_k": {"value": 40, "description": "Top K"},
            },
        }

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_get_session_by_id(self, mock_get_settings):
        from pipe.core.models.settings import Settings

        mock_settings = Settings(
            api_key="dummy",
            timezone="UTC",
            language="en",
            sessions_path=self.tmp_dir,
            parameters={
                "temperature": {"value": 0.5, "description": "Temp"},
                "top_p": {"value": 0.9, "description": "Top P"},
                "top_k": {"value": 40, "description": "Top K"},
            },
        )
        mock_get_settings.return_value = mock_settings

        result = get_session(session_id=self.test_session_id)

        self.assertEqual(result.session_id, self.test_session_id)
        self.assertEqual(result.turns_count, 2)
        self.assertIn("User: Hello", result.turns[0])
        self.assertIn("Assistant: Hi there!", result.turns[1])

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_get_session_ignores_env_var(self, mock_get_settings):
        """
        Tests that get_session requires explicit session_id and ignores environment
        variable.
        """
        from pipe.core.models.settings import Settings

        mock_settings = Settings(
            api_key="dummy",
            timezone="UTC",
            language="en",
            sessions_path=self.tmp_dir,
            parameters={
                "temperature": {"value": 0.5, "description": "Temp"},
                "top_p": {"value": 0.9, "description": "Top P"},
                "top_k": {"value": 40, "description": "Top K"},
            },
        )
        mock_get_settings.return_value = mock_settings

        os.environ["PIPE_SESSION_ID"] = self.test_session_id

        result = get_session()

        # Should return error even if env var is set
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error, "session_id is required.")

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_get_session_not_found(self, mock_get_settings):
        from pipe.core.models.settings import Settings

        mock_settings = Settings(
            api_key="dummy",
            timezone="UTC",
            language="en",
            sessions_path=self.tmp_dir,
            parameters={
                "temperature": {"value": 0.5, "description": "Temp"},
                "top_p": {"value": 0.9, "description": "Top P"},
                "top_k": {"value": 40, "description": "Top K"},
            },
        )
        mock_get_settings.return_value = mock_settings

        result = get_session(session_id="non_existent")

        self.assertIsNotNone(result.error)
        self.assertIn("not found", result.error)

    def test_get_session_no_id_no_env(self):
        result = get_session()

        self.assertIsNotNone(result.error)
        self.assertEqual(result.error, "session_id is required.")
