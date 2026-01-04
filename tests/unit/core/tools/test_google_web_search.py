"""Unit tests for google_web_search tool."""

import subprocess
import sys
from unittest.mock import MagicMock, patch

from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.google_web_search import google_web_search


class TestGoogleWebSearch:
    """Test google_web_search function."""

    def test_google_web_search_empty_query(self):
        """Test that calling with an empty query returns an error."""
        result = google_web_search("")
        assert isinstance(result, ToolResult)
        assert result.error == "google_web_search called without a query."
        assert result.data is None

    @patch("pipe.core.tools.google_web_search.get_project_root")
    @patch("pipe.core.tools.google_web_search.subprocess.run")
    def test_google_web_search_success(self, mock_run, mock_get_root):
        """Test successful web search execution."""
        mock_get_root.return_value = "/mock/project/root"
        mock_process = MagicMock()
        mock_process.stdout = "Search results content"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        query = "test query"
        result = google_web_search(query)

        assert result.is_success
        assert result.data is not None
        assert result.data["content"] == "Search results content"

        # Verify command construction
        expected_src_path = "/mock/project/root/src"
        expected_agent_path = "/mock/project/root/src/pipe/core/agents/search_agent.py"
        expected_command = (
            f"PYTHONPATH={expected_src_path} {sys.executable} {expected_agent_path} "
            f'"{query}"'
        )

        mock_run.assert_called_once_with(
            expected_command, shell=True, capture_output=True, text=True, check=True
        )

    @patch("pipe.core.tools.google_web_search.get_project_root")
    @patch("pipe.core.tools.google_web_search.subprocess.run")
    def test_google_web_search_called_process_error(self, mock_run, mock_get_root):
        """Test handling of subprocess.CalledProcessError."""
        mock_get_root.return_value = "/mock/project/root"
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="some command", stderr="Execution failed"
        )

        result = google_web_search("test query")

        assert not result.is_success
        assert "Failed to execute search agent: Execution failed" in result.error

    @patch("pipe.core.tools.google_web_search.get_project_root")
    @patch("pipe.core.tools.google_web_search.subprocess.run")
    def test_google_web_search_general_exception(self, mock_run, mock_get_root):
        """Test handling of general exceptions."""
        mock_get_root.return_value = "/mock/project/root"
        mock_run.side_effect = Exception("Unexpected error")

        result = google_web_search("test query")

        assert not result.is_success
        assert "Failed to execute search agent: Unexpected error" in result.error

    @patch("pipe.core.tools.google_web_search.get_project_root")
    @patch("pipe.core.tools.google_web_search.subprocess.run")
    @patch("builtins.print")
    def test_google_web_search_with_stderr(self, mock_print, mock_run, mock_get_root):
        """Test that stderr from the agent is printed to sys.stderr."""
        mock_get_root.return_value = "/mock/project/root"
        mock_process = MagicMock()
        mock_process.stdout = "Results"
        mock_process.stderr = "Warning message"
        mock_run.return_value = mock_process

        google_web_search("test query")

        mock_print.assert_called_once_with(
            "Search agent stderr: Warning message", file=sys.stderr
        )
