"""Unit tests for ts_condition_analyzer tool."""

import json
import subprocess
from unittest.mock import MagicMock, patch

from pipe.core.tools.ts_condition_analyzer import (
    AnalyzeConditionResult,
    BranchInfo,
    FunctionAnalysis,
    MockCandidate,
    ts_condition_analyzer,
)


class TestTsConditionAnalyzer:
    """Tests for ts_condition_analyzer function."""

    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_node_modules_not_allowed(self, mock_normpath):
        """Test that paths containing node_modules are rejected."""
        mock_normpath.return_value = "/path/to/node_modules/file.ts"
        result = ts_condition_analyzer("node_modules/file.ts")

        assert result.is_success is False
        assert "node_modules" in result.error

    @patch("pipe.core.tools.ts_condition_analyzer.os.path.exists")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_file_not_found(self, mock_normpath, mock_exists):
        """Test that non-existent files return an error."""
        mock_normpath.return_value = "/path/to/missing.ts"
        mock_exists.return_value = False

        result = ts_condition_analyzer("missing.ts")

        assert result.is_success is False
        assert "File not found" in result.error

    @patch("pipe.core.tools.ts_condition_analyzer.os.path.exists")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_invalid_extension(self, mock_normpath, mock_exists):
        """Test that non-TypeScript files are rejected."""
        mock_normpath.return_value = "/path/to/file.txt"
        mock_exists.return_value = True

        result = ts_condition_analyzer("file.txt")

        assert result.is_success is False
        assert "Not a TypeScript file" in result.error

    @patch("pipe.core.tools.ts_condition_analyzer.subprocess.run")
    @patch("pipe.core.tools.ts_condition_analyzer.get_project_root")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.abspath")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.exists")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_successful_analysis(
        self,
        mock_normpath,
        mock_exists,
        mock_abspath,
        mock_get_root,
        mock_run,
    ):
        """Test successful analysis of a TypeScript file."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.return_value = "/project"

        # Mock subprocess output
        mock_output = {
            "file_path": "/project/src/file.ts",
            "functions": [
                {
                    "name": "testFunc",
                    "lineno": 10,
                    "end_lineno": 20,
                    "parameters": ["a", "b"],
                    "branches": [
                        {
                            "type": "if",
                            "lineno": 12,
                            "end_lineno": 15,
                            "condition_code": "a > 0",
                        }
                    ],
                    "mock_candidates": [
                        {
                            "name": "this.repo.save",
                            "lineno": 14,
                            "is_method_call": True,
                        }
                    ],
                    "cyclomatic_complexity": 2,
                    "is_async": True,
                    "is_arrow_function": False,
                }
            ],
        }
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_output)
        mock_run.return_value = mock_process

        result = ts_condition_analyzer("src/file.ts")

        assert result.is_success is True
        assert isinstance(result.data, AnalyzeConditionResult)
        assert result.data.file_path == "/project/src/file.ts"
        assert len(result.data.functions) == 1

        func = result.data.functions[0]
        assert isinstance(func, FunctionAnalysis)
        assert func.name == "testFunc"
        assert func.lineno == 10
        assert func.is_async is True
        assert len(func.branches) == 1
        assert isinstance(func.branches[0], BranchInfo)
        assert func.branches[0].type == "if"
        assert len(func.mock_candidates) == 1
        assert isinstance(func.mock_candidates[0], MockCandidate)
        assert func.mock_candidates[0].name == "this.repo.save"

    @patch("pipe.core.tools.ts_condition_analyzer.subprocess.run")
    @patch("pipe.core.tools.ts_condition_analyzer.get_project_root")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.abspath")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.exists")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_function_not_found(
        self,
        mock_normpath,
        mock_exists,
        mock_abspath,
        mock_get_root,
        mock_run,
    ):
        """Test error when specified function is not found in the file."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.return_value = "/project"

        mock_output = {"file_path": "/project/src/file.ts", "functions": []}
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_output)
        mock_run.return_value = mock_process

        result = ts_condition_analyzer("src/file.ts", function_name="missingFunc")

        assert result.is_success is False
        assert "Function 'missingFunc' not found" in result.error

    @patch("pipe.core.tools.ts_condition_analyzer.subprocess.run")
    @patch("pipe.core.tools.ts_condition_analyzer.get_project_root")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.abspath")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.exists")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_subprocess_error(
        self,
        mock_normpath,
        mock_exists,
        mock_abspath,
        mock_get_root,
        mock_run,
    ):
        """Test handling of subprocess execution failure."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.return_value = "/project"

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="npx ts-node ...", stderr="TS Error"
        )

        result = ts_condition_analyzer("src/file.ts")

        assert result.is_success is False
        assert "ts_analyzer.ts failed" in result.error
        assert "TS Error" in result.error

    @patch("pipe.core.tools.ts_condition_analyzer.subprocess.run")
    @patch("pipe.core.tools.ts_condition_analyzer.get_project_root")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.abspath")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.exists")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_json_decode_error(
        self,
        mock_normpath,
        mock_exists,
        mock_abspath,
        mock_get_root,
        mock_run,
    ):
        """Test handling of invalid JSON output from subprocess."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.return_value = "/project"

        mock_process = MagicMock()
        mock_process.stdout = "invalid json"
        mock_run.return_value = mock_process

        result = ts_condition_analyzer("src/file.ts")

        assert result.is_success is False
        assert "Failed to parse JSON output" in result.error

    @patch("pipe.core.tools.ts_condition_analyzer.subprocess.run")
    @patch("pipe.core.tools.ts_condition_analyzer.get_project_root")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.abspath")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.exists")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_unexpected_error(
        self,
        mock_normpath,
        mock_exists,
        mock_abspath,
        mock_get_root,
        mock_run,
    ):
        """Test handling of unexpected exceptions."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.return_value = "/project"

        mock_run.side_effect = Exception("Unexpected")

        result = ts_condition_analyzer("src/file.ts")

        assert result.is_success is False
        assert "An unexpected error occurred" in result.error
        assert "Unexpected" in result.error

    @patch("pipe.core.tools.ts_condition_analyzer.subprocess.run")
    @patch("pipe.core.tools.ts_condition_analyzer.get_project_root")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.abspath")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.exists")
    @patch("pipe.core.tools.ts_condition_analyzer.os.path.normpath")
    def test_analyzer_reported_error(
        self,
        mock_normpath,
        mock_exists,
        mock_abspath,
        mock_get_root,
        mock_run,
    ):
        """Test handling of error reported within the JSON output."""
        mock_normpath.return_value = "/project/src/file.ts"
        mock_exists.return_value = True
        mock_abspath.return_value = "/project/src/file.ts"
        mock_get_root.return_value = "/project"

        mock_output = {"error": "Internal analyzer error"}
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_output)
        mock_run.return_value = mock_process

        result = ts_condition_analyzer("src/file.ts")

        assert result.is_success is False
        assert "Internal analyzer error" in result.error
