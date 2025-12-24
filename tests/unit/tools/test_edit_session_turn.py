import json
import os
import shutil
import unittest
import warnings
from unittest.mock import patch

from pipe.core.models.session import Session
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn
from pipe.core.tools.edit_session_turn import edit_session_turn

from tests.factories.models.settings_factory import create_test_settings


class TestEditSessionTurn(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

        self.project_root = os.getcwd()
        self.tmp_dir = os.path.join(self.project_root, ".gemini/tmp/test_sessions")
        self.sessions_dir = os.path.join(self.tmp_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)

        self.session_id = "test_session_edit"
        self.session_file = os.path.join(self.sessions_dir, f"{self.session_id}.json")

        # Create a dummy session
        self.session_data = Session(
            session_id=self.session_id,
            turns=[
                UserTaskTurn(
                    type="user_task",
                    instruction="Original instruction",
                    timestamp="2023-01-01T00:00:00Z",
                ),
                ModelResponseTurn(
                    type="model_response",
                    content="Original content",
                    timestamp="2023-01-01T00:00:01Z",
                ),
            ],
            created_at="2023-01-01T00:00:00Z",
            purpose="Test purpose",
            background="Test background",
            roles=[],
        )

        with open(self.session_file, "w") as f:
            f.write(self.session_data.model_dump_json())

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_edit_user_task_turn(self, mock_get_settings):
        mock_get_settings.return_value = create_test_settings(
            sessions_path=self.sessions_dir,
        )
        new_instruction = "Updated instruction"
        result = edit_session_turn(
            session_id=self.session_id, turn=1, new_content=new_instruction
        )
        self.assertIn("Successfully edited turn 1", result.data.message)

        # Verify change
        with open(self.session_file) as f:
            data = json.load(f)
            self.assertEqual(data["turns"][0]["instruction"], new_instruction)

        # Verify backup
        backups_dir = os.path.join(self.sessions_dir, "backups")
        self.assertTrue(os.path.exists(backups_dir))
        self.assertTrue(len(os.listdir(backups_dir)) > 0)

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_edit_model_response_turn(self, mock_get_settings):
        mock_get_settings.return_value = create_test_settings(
            sessions_path=self.sessions_dir,
        )
        new_content = "Updated content"
        result = edit_session_turn(
            session_id=self.session_id, turn=2, new_content=new_content
        )

        self.assertIn("Successfully edited turn 2", result.data.message)

        # Verify change
        with open(self.session_file) as f:
            data = json.load(f)
            self.assertEqual(data["turns"][1]["content"], new_content)

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_edit_invalid_turn_index(self, mock_get_settings):
        mock_get_settings.return_value = create_test_settings(
            sessions_path=self.sessions_dir,
        )
        result = edit_session_turn(
            session_id=self.session_id, turn=99, new_content="Fail"
        )
        self.assertIsNotNone(result.error)
        self.assertIn("not found", result.error)

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_edit_via_env_var(self, mock_get_settings):
        mock_get_settings.return_value = create_test_settings(
            sessions_path=self.sessions_dir,
        )
        os.environ["PIPE_SESSION_ID"] = self.session_id
        new_instruction = "Env var instruction"
        result = edit_session_turn(turn=1, new_content=new_instruction)

        self.assertIn("Successfully edited turn 1", result.data.message)

        with open(self.session_file) as f:
            data = json.load(f)
            self.assertEqual(data["turns"][0]["instruction"], new_instruction)


if __name__ == "__main__":
    unittest.main()
