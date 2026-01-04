"""Unit tests for ts_get_type_definitions tool."""

import json
import subprocess
from unittest.mock import MagicMock, patch

from pipe.core.tools.ts_get_type_definitions import ts_get_type_definitions


class TestTsGetTypeDefinitions:
    """Tests for ts_get_type_definitions function."""

    def test_node_modules_restriction(self):
        """Test that operation on node_modules is restricted."""
        result = ts_get_type_definitions("path/to/node_modules/file.ts", "MySymbol")
        assert result.is_success is False
        assert "node_modules" in result.error

    @patch("pipe.core.tools.ts_get_type_definitions.os.path.exists")
    def test_file_not_found(self, mock_exists):
        """Test handling of non-existent file."""
        mock_exists.return_value = False
        result = ts_get_type_definitions("non_existent.ts", "MySymbol")
        assert result.is_success is False
        assert "File not found" in result.error

    @patch("pipe.core.tools.ts_get_type_definitions.os.path.exists")
    @patch("pipe.core.tools.ts_get_type_definitions.os.path.abspath")
    @patch("pipe.core.tools.ts_get_type_definitions.get_project_root")
    @patch("pipe.core.tools.ts_get_type_definitions.subprocess.run")
    def test_successful_execution(
        self, mock_run, mock_get_root, mock_abspath, mock_exists
    ):
        """Test successful extraction of type definitions."""
        mock_exists.return_value = True
        mock_abspath.return_value = "/abs/path/to/file.ts"
        mock_get_root.return_value = "/project/root"

        mock_process = MagicMock()
        mock_process.stdout = json.dumps({"MySymbol": "type MySymbol = string;"})
        mock_run.return_value = mock_process

        result = ts_get_type_definitions("/abs/path/to/file.ts", "MySymbol")

        assert result.is_success is True
        assert result.data["type_definitions"] == {
            "MySymbol": "type MySymbol = string;"
        }
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "npx" in args[0]
        assert "ts-node" in args[0]
        assert "/abs/path/to/file.ts" in args[0]
        assert "MySymbol" in args[0]
        assert kwargs["cwd"] == "/project/root"

    @patch("pipe.core.tools.ts_get_type_definitions.os.path.exists")
    @patch("pipe.core.tools.ts_get_type_definitions.os.path.abspath")
    @patch("pipe.core.tools.ts_get_type_definitions.get_project_root")
    @patch("pipe.core.tools.ts_get_type_definitions.subprocess.run")
    def test_ts_analyzer_error_in_output(
        self, mock_run, mock_get_root, mock_abspath, mock_exists
    ):
        """Test handling of error returned by ts_analyzer.ts."""
        mock_exists.return_value = True
        mock_abspath.return_value = "/abs/path/to/file.ts"
        mock_get_root.return_value = "/project/root"

        mock_process = MagicMock()
        mock_process.stdout = json.dumps({"error": "Symbol not found"})
        mock_run.return_value = mock_process

        result = ts_get_type_definitions("/abs/path/to/file.ts", "MySymbol")

        assert result.is_success is False
        assert result.error == "Symbol not found"

    @patch("pipe.core.tools.ts_get_type_definitions.os.path.exists")
    @patch("pipe.core.tools.ts_get_type_definitions.os.path.abspath")
    @patch("pipe.core.tools.ts_get_type_definitions.get_project_root")
    @patch("pipe.core.tools.ts_get_type_definitions.subprocess.run")
    def test_subprocess_failure(
        self, mock_run, mock_get_root, mock_abspath, mock_exists
    ):
        """Test handling of subprocess failure."""
        mock_exists.return_value = True
        mock_abspath.return_value = "/abs/path/to/file.ts"
        mock_get_root.return_value = "/project/root"

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="npx ts-node ...", stderr="Compilation error"
        )

        result = ts_get_type_definitions("/abs/path/to/file.ts", "MySymbol")

        assert result.is_success is False
        assert "ts_analyzer.ts failed: Compilation error" in result.error

    @patch("pipe.core.tools.ts_get_type_definitions.os.path.exists")
    @patch("pipe.core.tools.ts_get_type_definitions.os.path.abspath")
    @patch("pipe.core.tools.ts_get_type_definitions.get_project_root")
    @patch("pipe.core.tools.ts_get_type_definitions.subprocess.run")
    def test_json_decode_error(
        self, mock_run, mock_get_root, mock_abspath, mock_exists
    ):
        """Test handling of invalid JSON output."""
        mock_exists.return_value = True
        mock_abspath.return_value = "/abs/path/to/file.ts"
        mock_get_root.return_value = "/project/root"

        mock_process = MagicMock()
        mock_process.stdout = "Invalid JSON"
        mock_run.return_value = mock_process

        result = ts_get_type_definitions("/abs/path/to/file.ts", "MySymbol")

        assert result.is_success is False
        assert "Failed to parse JSON output" in result.error

    @patch("pipe.core.tools.ts_get_type_definitions.os.path.exists")
    @patch("pipe.core.tools.ts_get_type_definitions.get_project_root")
    def test_unexpected_error(self, mock_get_root, mock_exists):
        """Test handling of unexpected exceptions."""
        mock_exists.return_value = True
        mock_get_root.side_effect = Exception("Unexpected")
        result = ts_get_type_definitions("file.ts", "MySymbol")
        assert result.is_success is False
        assert "An unexpected error occurred: Unexpected" in result.error
