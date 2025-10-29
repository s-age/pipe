import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.agents.gemini_cli import call_gemini_cli
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings
from pipe.core.services.session_service import SessionService


class TestGeminiCliIntegration(unittest.TestCase):
    def setUp(self):
        """Set up a real SessionService instance using the real project root,
        but redirect the sessions directory to a temporary location."""
        # Use the real project root to find templates
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )

        # Create a temporary directory for sessions
        self.temp_sessions_dir = tempfile.mkdtemp()

        # Create dummy settings
        settings_data = {
            "model": "gemini-test-model",
            "search_model": "gemini-test-model",
            "context_limit": 10000,
            "api_mode": "gemini-cli",
            "language": "en",
            "yolo": True,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.1, "description": "t"},
                "top_p": {"value": 0.2, "description": "p"},
                "top_k": {"value": 10, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)

        # Instantiate the real service, then override the sessions path
        self.session_service = SessionService(
            project_root=self.project_root, settings=self.settings
        )
        self.session_service.sessions_dir = self.temp_sessions_dir
        self.session_service.index_path = os.path.join(
            self.temp_sessions_dir, "index.json"
        )

    def tearDown(self):
        """Clean up the temporary sessions directory."""
        shutil.rmtree(self.temp_sessions_dir)

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    def test_call_gemini_cli_with_real_session_service(self, mock_popen):
        """
        Tests that call_gemini_cli works correctly with a real, prepared
        SessionService instance.
        """
        # Mock the subprocess call
        mock_process = MagicMock()
        mock_process.stdout.readline.return_value = ""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # 1. Prepare arguments as if they came from the command line
        args = TaktArgs(
            purpose="Test CLI call", background="BG", instruction="Test instruction"
        )

        # 2. Prepare the session service, which sets up the internal state
        self.session_service.prepare_session_for_takt(args)

        # 3. Call the function to be tested
        call_gemini_cli(self.session_service)

        # 4. Assert that Popen was called correctly
        mock_popen.assert_called_once()

        command_args, _ = mock_popen.call_args
        command = command_args[0]

        # Verify the command structure
        self.assertIn("gemini", command)
        self.assertIn("-y", command)
        self.assertIn("-m", command)
        self.assertIn("gemini-test-model", command)

        # Verify the prompt content
        prompt_string = command[command.index("-p") + 1]
        prompt_data = json.loads(prompt_string)

        expected_description = (
            "This structured prompt guides your response. First, understand the "
            "core instructions: `main_instruction` defines your thinking "
            "process. Next, identify the immediate objective from `current_task` "
            "and `todos`. Then, gather all context required to execute the task "
            "by processing `session_goal`, `roles`, `constraints`, "
            "`conversation_history`, and `file_references` in that order. "
            "Finally, execute the `current_task` by synthesizing all gathered "
            "information."
        )

        self.assertEqual(prompt_data["session_goal"]["purpose"], "Test CLI call")
        self.assertEqual(prompt_data["description"], expected_description)
        self.assertEqual(prompt_data["current_task"]["instruction"], "Test instruction")


if __name__ == "__main__":
    unittest.main()
