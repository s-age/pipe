import os
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.tools.google_web_search import google_web_search


class TestGoogleWebSearchTool(unittest.TestCase):
    @patch("pipe.core.tools.google_web_search.subprocess.run")
    def test_google_web_search_executes_agent_and_returns_output(
        self, mock_subprocess_run
    ):
        """
        Tests that the google_web_search tool executes the search agent
        and returns its stdout.
        """
        # 1. Setup: Mock the subprocess.run to return a successful result
        mock_process = MagicMock()
        mock_process.stdout = "This is the search result."
        mock_process.stderr = ""
        mock_subprocess_run.return_value = mock_process

        query = "What is the capital of France?"

        # 2. Run the tool
        result = google_web_search(query=query)

        # 3. Assertions
        self.assertTrue(mock_subprocess_run.called)

        # Construct the expected command for assertion
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        src_path = os.path.join(project_root, "src")
        agent_path = os.path.join(src_path, "pipe", "core", "agents", "search_agent.py")
        expected_command = (
            f'PYTHONPATH={src_path} {sys.executable} {agent_path} "{query}"'
        )

        mock_subprocess_run.assert_called_once_with(
            expected_command, shell=True, capture_output=True, text=True, check=True
        )

        self.assertIn("content", result)
        self.assertEqual(result["content"], "This is the search result.")

    @patch("pipe.core.tools.google_web_search.subprocess.run")
    def test_google_web_search_handles_subprocess_error(self, mock_subprocess_run):
        """
        Tests that the tool handles exceptions from the subprocess call gracefully.
        """
        # 1. Setup: Mock the subprocess.run to raise an exception
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="test command", stderr="Subprocess Failure"
        )

        # 2. Run the tool
        result = google_web_search(query="test query")

        # 3. Assertions
        self.assertIn("error", result)
        self.assertIn(
            "Failed to execute search agent: Subprocess Failure", result["error"]
        )


if __name__ == "__main__":
    unittest.main()
