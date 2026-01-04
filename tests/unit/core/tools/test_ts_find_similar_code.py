"""Unit tests for ts_find_similar_code tool."""

import json
from unittest.mock import MagicMock, patch

from pipe.core.models.results.ts_find_similar_code_result import TSFindSimilarCodeResult
from pipe.core.tools.ts_find_similar_code import ts_find_similar_code


class TestTSFindSimilarCode:
    """Tests for ts_find_similar_code function."""

    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_node_modules_restriction(self, mock_get_root):
        """Test that operation on node_modules is not allowed."""
        mock_get_root.return_value = "/project"

        # Base file in node_modules
        result = ts_find_similar_code(
            base_file_path="/project/node_modules/file.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is False
        assert "node_modules" in result.error

        # Search directory in node_modules
        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
            search_directory="/project/node_modules",
        )
        assert result.is_success is False
        assert "node_modules" in result.error

    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_base_file_not_found(self, mock_get_root, mock_exists):
        """Test behavior when base file does not exist."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = False

        result = ts_find_similar_code(
            base_file_path="/project/src/missing.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is False
        assert "Base file not found" in result.error

    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_search_directory_not_found(self, mock_get_root, mock_exists, mock_isdir):
        """Test behavior when search directory does not exist."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = False

        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
            search_directory="/project/missing_dir",
        )
        assert result.is_success is False
        assert "Search directory not found" in result.error

    @patch("pipe.core.tools.ts_find_similar_code.subprocess.run")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_subprocess_failure(self, mock_get_root, mock_exists, mock_isdir, mock_run):
        """Test behavior when ts_analyzer.ts fails."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = "Analyzer error"
        mock_run.return_value = mock_process

        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is False
        assert "Analyzer error" in result.error

    @patch("pipe.core.tools.ts_find_similar_code.subprocess.run")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_json_decode_error(self, mock_get_root, mock_exists, mock_isdir, mock_run):
        """Test behavior when analyzer output is invalid JSON."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Invalid JSON"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is False
        assert "Failed to parse JSON output" in result.error

    @patch("pipe.core.tools.ts_find_similar_code.subprocess.run")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_unexpected_output_format_list(
        self, mock_get_root, mock_exists, mock_isdir, mock_run
    ):
        """Test behavior when analyzer returns a list instead of a dict."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = json.dumps([{"item": 1}])
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is False
        assert "Unexpected output format" in result.error

    @patch("pipe.core.tools.ts_find_similar_code.subprocess.run")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_analyzer_error_in_output(
        self, mock_get_root, mock_exists, mock_isdir, mock_run
    ):
        """Test behavior when analyzer returns an error field in JSON."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = json.dumps({"error": "Internal analyzer error"})
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is False
        assert "Internal analyzer error" == result.error

    @patch("pipe.core.tools.ts_find_similar_code.subprocess.run")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_successful_execution(
        self, mock_get_root, mock_exists, mock_isdir, mock_run
    ):
        """Test successful execution and parsing of results."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = json.dumps(
            {
                "base_snippet": "class Base {}",
                "base_type_definitions": {"Base": "interface Base {}"},
                "matches": [
                    {
                        "file": "src/other.ts",
                        "symbol": "Other",
                        "similarity": 0.85,
                        "snippet": "class Other {}",
                    }
                ],
            }
        )
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
        )

        assert result.is_success is True
        assert isinstance(result.data, TSFindSimilarCodeResult)
        assert result.data.base_snippet == "class Base {}"
        assert result.data.base_type_definitions == {"Base": "interface Base {}"}
        assert len(result.data.matches) == 1
        assert result.data.matches[0].symbol == "Other"
        assert result.data.matches[0].similarity == 0.85

    @patch("pipe.core.tools.ts_find_similar_code.subprocess.run")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_unexpected_exception(
        self, mock_get_root, mock_exists, mock_isdir, mock_run
    ):
        """Test catch-all exception handling."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        # Raise exception during subprocess.run which is inside the try block
        mock_run.side_effect = Exception("Unexpected boom")

        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is False
        assert "An unexpected error occurred" in result.error
        assert "Unexpected boom" in result.error

    @patch("pipe.core.tools.ts_find_similar_code.subprocess.run")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_stderr_output_with_success(
        self, mock_get_root, mock_exists, mock_isdir, mock_run
    ):
        """Test that stderr is printed even if execution is successful."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = json.dumps({"matches": []})
        mock_process.stderr = "Some debug info"
        mock_run.return_value = mock_process

        # We just want to make sure it doesn't crash and covers the line
        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is True

    @patch("pipe.core.tools.ts_find_similar_code.subprocess.run")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.isdir")
    @patch("pipe.core.tools.ts_find_similar_code.os.path.exists")
    @patch("pipe.core.tools.ts_find_similar_code.get_project_root")
    def test_unexpected_output_type(
        self, mock_get_root, mock_exists, mock_isdir, mock_run
    ):
        """Test behavior when analyzer returns an unexpected type (not dict/list)."""
        mock_get_root.return_value = "/project"
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "123"  # JSON int
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = ts_find_similar_code(
            base_file_path="/project/src/file.ts",
            symbol_name="MySymbol",
        )
        assert result.is_success is False
        assert "Unexpected output type" in result.error
