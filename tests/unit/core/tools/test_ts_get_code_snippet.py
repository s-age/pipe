"""Unit tests for ts_get_code_snippet tool."""

import subprocess
from unittest.mock import MagicMock, patch

from pipe.core.tools.ts_get_code_snippet import ts_get_code_snippet


class TestTsGetCodeSnippet:
    """Tests for ts_get_code_snippet function."""

    @patch("pipe.core.tools.ts_get_code_snippet.os.path.normpath")
    def test_node_modules_restriction(self, mock_normpath: MagicMock) -> None:
        """Test that operation on node_modules is restricted."""
        mock_normpath.return_value = "/project/node_modules/file.ts"

        result = ts_get_code_snippet("node_modules/file.ts", "MyClass")

        assert result.is_success is False
        assert result.error is not None
        assert "node_modules" in result.error

    @patch("pipe.core.tools.ts_get_code_snippet.os.path.normpath")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.exists")
    def test_file_not_found(
        self, mock_exists: MagicMock, mock_normpath: MagicMock
    ) -> None:
        """Test handling of non-existent file."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = False

        result = ts_get_code_snippet("src/file.ts", "MyClass")

        assert result.is_success is False
        assert result.error is not None
        assert "File not found" in result.error

    @patch("pipe.core.tools.ts_get_code_snippet.os.path.normpath")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.exists")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.abspath")
    @patch("pipe.core.tools.ts_get_code_snippet.get_project_root")
    @patch("pipe.core.tools.ts_get_code_snippet.subprocess.run")
    def test_successful_extraction(
        self,
        mock_run: MagicMock,
        mock_get_root: MagicMock,
        mock_abspath: MagicMock,
        mock_exists: MagicMock,
        mock_normpath: MagicMock,
    ) -> None:
        """Test successful code snippet extraction."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.side_effect = lambda x: x if x.startswith("/") else f"/project/{x}"
        mock_get_root.return_value = "/project"

        mock_process = MagicMock()
        mock_process.stdout = "class MyClass { ... }"
        mock_run.return_value = mock_process

        result = ts_get_code_snippet("src/file.ts", "MyClass")

        assert result.is_success is True
        assert result.data is not None
        assert result.data["snippet"] == "class MyClass { ... }"
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        command = args[0]
        assert "get_code_snippet" in command
        assert "MyClass" in command
        assert kwargs["cwd"] == "/project"

    @patch("pipe.core.tools.ts_get_code_snippet.os.path.normpath")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.exists")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.abspath")
    @patch("pipe.core.tools.ts_get_code_snippet.get_project_root")
    @patch("pipe.core.tools.ts_get_code_snippet.subprocess.run")
    def test_no_snippet_found(
        self,
        mock_run: MagicMock,
        mock_get_root: MagicMock,
        mock_abspath: MagicMock,
        mock_exists: MagicMock,
        mock_normpath: MagicMock,
    ) -> None:
        """Test when no snippet is found by the analyzer."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.return_value = "/project"

        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_run.return_value = mock_process

        result = ts_get_code_snippet("src/file.ts", "MyClass")

        assert result.is_success is False
        assert result.error is not None
        assert "No code snippet found" in result.error

    @patch("pipe.core.tools.ts_get_code_snippet.os.path.normpath")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.exists")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.abspath")
    @patch("pipe.core.tools.ts_get_code_snippet.get_project_root")
    @patch("pipe.core.tools.ts_get_code_snippet.subprocess.run")
    def test_subprocess_error(
        self,
        mock_run: MagicMock,
        mock_get_root: MagicMock,
        mock_abspath: MagicMock,
        mock_exists: MagicMock,
        mock_normpath: MagicMock,
    ) -> None:
        """Test handling of subprocess failure."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.return_value = "/project"

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="npx ...", stderr="Analyzer error"
        )

        result = ts_get_code_snippet("src/file.ts", "MyClass")

        assert result.is_success is False
        assert result.error is not None
        assert "ts_analyzer.ts failed: Analyzer error" in result.error

    @patch("pipe.core.tools.ts_get_code_snippet.os.path.normpath")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.exists")
    @patch("pipe.core.tools.ts_get_code_snippet.os.path.abspath")
    @patch("pipe.core.tools.ts_get_code_snippet.get_project_root")
    def test_unexpected_error(
        self,
        mock_get_root: MagicMock,
        mock_abspath: MagicMock,
        mock_exists: MagicMock,
        mock_normpath: MagicMock,
    ) -> None:
        """Test handling of unexpected exceptions."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.side_effect = Exception("Unexpected failure")

        result = ts_get_code_snippet("src/file.ts", "MyClass")

        assert result.is_success is False
        assert result.error is not None
        assert "An unexpected error occurred: Unexpected failure" in result.error
