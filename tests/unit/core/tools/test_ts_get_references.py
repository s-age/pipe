"""Unit tests for ts_get_references tool."""

import json
import subprocess
from unittest.mock import MagicMock, patch

from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.ts_get_references import ts_get_references


class TestTSGetReferences:
    """Tests for ts_get_references tool."""

    @patch("pipe.core.tools.ts_get_references.os.path.normpath")
    def test_node_modules_restriction(self, mock_normpath: MagicMock) -> None:
        """Test that operation on files within 'node_modules' is restricted."""
        mock_normpath.return_value = "/path/to/node_modules/file.ts"

        result = ts_get_references("node_modules/file.ts", "MySymbol")

        assert isinstance(result, ToolResult)
        assert result.is_success is False
        assert "node_modules" in result.error
        assert "not allowed" in result.error

    @patch("pipe.core.tools.ts_get_references.os.path.exists")
    @patch("pipe.core.tools.ts_get_references.os.path.normpath")
    def test_file_not_found(
        self, mock_normpath: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test that error is returned if file does not exist."""
        mock_normpath.return_value = "/path/to/non_existent.ts"
        mock_exists.return_value = False

        result = ts_get_references("non_existent.ts", "MySymbol")

        assert result.is_success is False
        assert "File not found" in result.error

    @patch("pipe.core.tools.ts_get_references.subprocess.run")
    @patch("pipe.core.tools.ts_get_references.get_project_root")
    @patch("pipe.core.tools.ts_get_references.os.path.exists")
    @patch("pipe.core.tools.ts_get_references.os.path.normpath")
    @patch("pipe.core.tools.ts_get_references.os.path.abspath")
    def test_successful_execution(
        self,
        mock_abspath: MagicMock,
        mock_normpath: MagicMock,
        mock_exists: MagicMock,
        mock_get_root: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test successful retrieval of TypeScript references."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        # Mock abspath to return different values for different inputs
        mock_abspath.side_effect = lambda x: f"/abs/{x}" if "ts_analyzer.ts" in x else x
        mock_get_root.return_value = "/project"

        mock_output = [
            {"file": "file.ts", "line": 10, "column": 5, "text": "symbol usage"}
        ]
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_output)
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = ts_get_references("file.ts", "MySymbol")

        assert result.is_success is True
        assert result.data is not None
        assert result.data["symbol_name"] == "MySymbol"
        assert result.data["reference_count"] == 1
        assert result.data["references"] == mock_output

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        command = args[0]
        assert command[0] == "npx"
        assert command[1] == "ts-node"
        assert "ts_analyzer.ts" in command[2]
        assert command[3] == "get_references"
        assert command[4] == "file.ts"
        assert command[5] == "MySymbol"
        assert kwargs["cwd"] == "/project"

    @patch("pipe.core.tools.ts_get_references.subprocess.run")
    @patch("pipe.core.tools.ts_get_references.get_project_root")
    @patch("pipe.core.tools.ts_get_references.os.path.exists")
    @patch("pipe.core.tools.ts_get_references.os.path.normpath")
    def test_ts_analyzer_error_in_output(
        self,
        mock_normpath: MagicMock,
        mock_exists: MagicMock,
        mock_get_root: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test when ts_analyzer.ts returns an error in its JSON output."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_get_root.return_value = "/project"

        mock_process = MagicMock()
        mock_process.stdout = json.dumps({"error": "Something went wrong in analyzer"})
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = ts_get_references("file.ts", "MySymbol")

        assert result.is_success is False
        assert result.error == "Something went wrong in analyzer"

    @patch("pipe.core.tools.ts_get_references.subprocess.run")
    @patch("pipe.core.tools.ts_get_references.get_project_root")
    @patch("pipe.core.tools.ts_get_references.os.path.exists")
    @patch("pipe.core.tools.ts_get_references.os.path.normpath")
    def test_subprocess_failure(
        self,
        mock_normpath: MagicMock,
        mock_exists: MagicMock,
        mock_get_root: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test handling of subprocess.CalledProcessError."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_get_root.return_value = "/project"

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="npx ...", stderr="Subprocess error message"
        )

        result = ts_get_references("file.ts", "MySymbol")

        assert result.is_success is False
        assert result.error is not None
        assert "ts_analyzer.ts failed" in result.error
        assert "Subprocess error message" in result.error

    @patch("pipe.core.tools.ts_get_references.subprocess.run")
    @patch("pipe.core.tools.ts_get_references.get_project_root")
    @patch("pipe.core.tools.ts_get_references.os.path.exists")
    @patch("pipe.core.tools.ts_get_references.os.path.normpath")
    def test_json_decode_error(
        self,
        mock_normpath: MagicMock,
        mock_exists: MagicMock,
        mock_get_root: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test handling of json.JSONDecodeError."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_get_root.return_value = "/project"

        mock_process = MagicMock()
        mock_process.stdout = "Invalid JSON"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = ts_get_references("file.ts", "MySymbol")

        assert result.is_success is False
        assert result.error is not None
        assert "Failed to parse JSON output" in result.error
        assert "Invalid JSON" in result.error

    @patch("pipe.core.tools.ts_get_references.subprocess.run")
    @patch("pipe.core.tools.ts_get_references.get_project_root")
    @patch("pipe.core.tools.ts_get_references.os.path.exists")
    @patch("pipe.core.tools.ts_get_references.os.path.normpath")
    def test_unexpected_exception(
        self,
        mock_normpath: MagicMock,
        mock_exists: MagicMock,
        mock_get_root: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test handling of unexpected exceptions."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_get_root.return_value = "/project"

        mock_run.side_effect = Exception("Unexpected boom")

        result = ts_get_references("file.ts", "MySymbol")

        assert result.is_success is False
        assert result.error is not None
        assert "An unexpected error occurred" in result.error
        assert "Unexpected boom" in result.error

    @patch("pipe.core.tools.ts_get_references.subprocess.run")
    @patch("pipe.core.tools.ts_get_references.get_project_root")
    @patch("pipe.core.tools.ts_get_references.os.path.exists")
    @patch("pipe.core.tools.ts_get_references.os.path.normpath")
    @patch("builtins.print")
    def test_stderr_debug_output(
        self,
        mock_print: MagicMock,
        mock_normpath: MagicMock,
        mock_exists: MagicMock,
        mock_get_root: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """Test that stderr output is printed as debug info."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_get_root.return_value = "/project"

        mock_process = MagicMock()
        mock_process.stdout = "[]"
        mock_process.stderr = "Some debug info"
        mock_run.return_value = mock_process

        result = ts_get_references("file.ts", "MySymbol")

        assert result.is_success is True
        mock_print.assert_called_once_with(
            "DEBUG (ts_analyzer.ts stderr): Some debug info"
        )
