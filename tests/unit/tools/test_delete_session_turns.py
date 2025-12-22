import json
import os
import shutil
import unittest
import warnings
from unittest.mock import patch

from pipe.core.tools.delete_session_turns import delete_session_turns

from tests.factories.models.settings_factory import create_test_settings


class TestDeleteSessionTurns(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

        self.test_session_id = "test_delete_turns_id"
        self.tmp_dir = "/tmp/pipe_tests/sessions"

        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.makedirs(self.tmp_dir, exist_ok=True)

        self.session_file = os.path.join(self.tmp_dir, f"{self.test_session_id}.json")

        # Create dummy session with turns
        self.initial_turns = [
            {"type": "user_task", "instruction": "turn 1"},
            {"type": "model_response", "content": "turn 2"},
            {"type": "user_task", "instruction": "turn 3"},
        ]

        with open(self.session_file, "w") as f:
            json.dump(
                {
                    "session_id": self.test_session_id,
                    "created_at": "2023-01-01T00:00:00",
                    "purpose": "test",
                    "background": "test",
                    "roles": [],
                    "turns": self.initial_turns,
                },
                f,
            )

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_delete_turns_success(self, mock_get_settings):
        # Mock settings
        mock_settings = create_test_settings(
            sessions_path=self.tmp_dir,
        )
        mock_get_settings.return_value = mock_settings

        # Delete turn 2 (index 1)
        result = delete_session_turns(session_id=self.test_session_id, turns=[2])

        self.assertIn("Successfully deleted", result.data.message)

        # Verify deletion
        with open(self.session_file) as f:
            data = json.load(f)
            turns = data["turns"]
            self.assertEqual(len(turns), 2)
            self.assertEqual(turns[0]["instruction"], "turn 1")
            self.assertEqual(turns[1]["instruction"], "turn 3")

    def test_missing_args(self):
        # Missing 'turns' should raise a TypeError
        with self.assertRaises(TypeError):
            delete_session_turns(session_id="some_id")

        # Missing 'session_id' should raise a TypeError
        with self.assertRaises(TypeError):
            delete_session_turns(turns=[1])
