import json
import os
import unittest
import warnings
from unittest.mock import patch

from pipe.core.tools.compress_session_turns import compress_session_turns

from tests.helpers.settings_factory import create_test_settings

# Ignore Pydantic warnings about 'Operation' class from google-genai
warnings.filterwarnings(
    "ignore", message='Field name ".*" shadows an attribute in parent "Operation";'
)


class TestCompressSessionTurns(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

        # Test settings
        self.test_session_id = "compress_tool_test"
        self.tmp_dir = "/tmp/pipe_tests/sessions"
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.session_file = os.path.join(self.tmp_dir, f"{self.test_session_id}.json")
        self.index_file = os.path.join(self.tmp_dir, "index.json")

        # Dummy session data
        self.initial_turns = [
            {
                "type": "user_task",
                "instruction": "turn 1",
                "timestamp": "2023-01-01T00:00:00Z",
            },
            {
                "type": "model_response",
                "content": "turn 2",
                "timestamp": "2023-01-01T00:00:01Z",
            },
            {
                "type": "user_task",
                "instruction": "turn 3",
                "timestamp": "2023-01-01T00:00:02Z",
            },
            {
                "type": "model_response",
                "content": "turn 4",
                "timestamp": "2023-01-01T00:00:03Z",
            },
            {
                "type": "user_task",
                "instruction": "turn 5",
                "timestamp": "2023-01-01T00:00:04Z",
            },
        ]

        session_data = {
            "session_id": self.test_session_id,
            "created_at": "2023-01-01T00:00:00Z",
            "purpose": "Test compression",
            "turns": self.initial_turns,
        }

        with open(self.session_file, "w") as f:
            json.dump(session_data, f)

        # Create empty index.json
        with open(self.index_file, "w") as f:
            json.dump({"sessions": {}}, f)

    def tearDown(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        if os.path.exists(self.session_file + ".lock"):
            try:
                os.remove(self.session_file + ".lock")
            except OSError:
                pass
        if os.path.exists(self.index_file):
            os.remove(self.index_file)
        if os.path.exists(self.index_file + ".lock"):
            try:
                os.remove(self.index_file + ".lock")
            except OSError:
                pass
        if "PIPE_SESSION_ID" in os.environ:
            del os.environ["PIPE_SESSION_ID"]

    @patch("pipe.core.factories.settings_factory.SettingsFactory.get_settings")
    def test_compress_turns_success(self, mock_get_settings):
        # Setup mocks
        mock_settings = create_test_settings(
            sessions_path=self.tmp_dir,
        )
        mock_get_settings.return_value = mock_settings

        result = compress_session_turns(
            session_id=self.test_session_id,
            start_turn=2,
            end_turn=4,
            summary_text="Summarized turns 2-4",
        )

        # If result has error, print it
        if result.error:
            print(f"Test failed with error: {result.error}")

        self.assertIsNotNone(result.data.message)
        self.assertIn("Successfully compressed", result.data.message)

        # Verify the file content
        with open(self.session_file) as f:
            data = json.load(f)
            turns = data["turns"]
            # We expect turn 1 (index 0), then compressed turn, then turn 5 (index 4)
            self.assertEqual(len(turns), 3)
            self.assertEqual(turns[0]["instruction"], "turn 1")
            self.assertEqual(turns[1]["type"], "compressed_history")
            self.assertEqual(turns[1]["content"], "Summarized turns 2-4")
            self.assertEqual(turns[2]["instruction"], "turn 5")


if __name__ == "__main__":
    unittest.main()
