"""Unit tests for ts_analyze_code tool."""

import json
import subprocess
from unittest.mock import MagicMock, patch

from pipe.core.tools.ts_analyze_code import (
    AnalyzeCodeResult,
    FileAnalysisResult,
    _parse_file_result,
    ts_analyze_code,
)


class TestTsAnalyzeCode:
    """Tests for ts_analyze_code function."""

    def test_node_modules_prohibited(self):
        """Test that operations on node_modules are prohibited."""
        result = ts_analyze_code("path/to/node_modules/file.ts")
        assert not result.is_success
        assert "node_modules" in result.error

    @patch("pipe.core.tools.ts_analyze_code.os.path.exists")
    def test_path_not_found(self, mock_exists):
        """Test handling of non-existent path."""
        mock_exists.return_value = False
        result = ts_analyze_code("non_existent.ts")
        assert not result.is_success
        assert "Path not found" in result.error

    @patch("pipe.core.tools.ts_analyze_code.os.path.exists")
    @patch("pipe.core.tools.ts_analyze_code.os.path.isfile")
    @patch("pipe.core.tools.ts_analyze_code.os.path.abspath")
    def test_invalid_file_extension(self, mock_abspath, mock_isfile, mock_exists):
        """Test that non-TypeScript files are rejected."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_abspath.side_effect = lambda x: x
        result = ts_analyze_code("test.txt")
        assert not result.is_success
        assert "Not a TypeScript file" in result.error

    @patch("pipe.core.tools.ts_analyze_code.get_project_root")
    @patch("pipe.core.tools.ts_analyze_code.subprocess.run")
    @patch("pipe.core.tools.ts_analyze_code.os.path.exists")
    @patch("pipe.core.tools.ts_analyze_code.os.path.isfile")
    @patch("pipe.core.tools.ts_analyze_code.os.path.abspath")
    def test_analyze_file_success(
        self, mock_abspath, mock_isfile, mock_exists, mock_run, mock_root
    ):
        """Test successful analysis of a single TypeScript file."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_abspath.side_effect = lambda x: x
        mock_root.return_value = "/project/root"

        mock_output = {
            "file_path": "test.ts",
            "imports": [],
            "exports": [],
            "classes": [],
            "interfaces": [],
            "type_aliases": [],
            "functions": [],
            "variables": [],
        }
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_output)
        mock_run.return_value = mock_process

        result = ts_analyze_code("test.ts")

        assert result.is_success
        assert isinstance(result.data, AnalyzeCodeResult)
        assert result.data.total_files == 1
        assert len(result.data.files) == 1
        assert result.data.files[0].file_path == "test.ts"
        mock_run.assert_called_once()
        assert "analyze_file" in mock_run.call_args[0][0]

    @patch("pipe.core.tools.ts_analyze_code.get_project_root")
    @patch("pipe.core.tools.ts_analyze_code.subprocess.run")
    @patch("pipe.core.tools.ts_analyze_code.os.path.exists")
    @patch("pipe.core.tools.ts_analyze_code.os.path.isfile")
    @patch("pipe.core.tools.ts_analyze_code.os.path.abspath")
    def test_analyze_directory_success(
        self, mock_abspath, mock_isfile, mock_exists, mock_run, mock_root
    ):
        """Test successful analysis of a directory."""
        mock_exists.return_value = True
        mock_isfile.return_value = False
        mock_abspath.side_effect = lambda x: x
        mock_root.return_value = "/project/root"

        mock_output = {
            "total_files": 2,
            "files": [
                {"file_path": "file1.ts"},
                {"file_path": "file2.ts"},
            ],
        }
        mock_process = MagicMock()
        mock_process.stdout = json.dumps(mock_output)
        mock_run.return_value = mock_process

        result = ts_analyze_code("src", max_files=50)

        assert result.is_success
        assert result.data.total_files == 2
        assert len(result.data.files) == 2
        mock_run.assert_called_once()
        assert "analyze_directory" in mock_run.call_args[0][0]
        assert "50" in mock_run.call_args[0][0]

    @patch("pipe.core.tools.ts_analyze_code.subprocess.run")
    @patch("pipe.core.tools.ts_analyze_code.os.path.exists")
    @patch("pipe.core.tools.ts_analyze_code.os.path.isfile")
    @patch("pipe.core.tools.ts_analyze_code.os.path.abspath")
    def test_analyzer_error_in_output(
        self, mock_abspath, mock_isfile, mock_exists, mock_run
    ):
        """Test handling of error message returned by the analyzer script."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_abspath.side_effect = lambda x: x

        mock_process = MagicMock()
        mock_process.stdout = json.dumps({"error": "Internal analyzer error"})
        mock_run.return_value = mock_process

        result = ts_analyze_code("test.ts")

        assert not result.is_success
        assert "Internal analyzer error" in result.error

    @patch("pipe.core.tools.ts_analyze_code.subprocess.run")
    @patch("pipe.core.tools.ts_analyze_code.os.path.exists")
    @patch("pipe.core.tools.ts_analyze_code.os.path.isfile")
    @patch("pipe.core.tools.ts_analyze_code.os.path.abspath")
    def test_subprocess_failure(self, mock_abspath, mock_isfile, mock_exists, mock_run):
        """Test handling of subprocess failure."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_abspath.side_effect = lambda x: x

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="npx ts-node ...", stderr="Subprocess failed"
        )

        result = ts_analyze_code("test.ts")

        assert not result.is_success
        assert "ts_analyzer.ts failed" in result.error
        assert "Subprocess failed" in result.error

    @patch("pipe.core.tools.ts_analyze_code.subprocess.run")
    @patch("pipe.core.tools.ts_analyze_code.os.path.exists")
    @patch("pipe.core.tools.ts_analyze_code.os.path.isfile")
    @patch("pipe.core.tools.ts_analyze_code.os.path.abspath")
    def test_json_decode_error(self, mock_abspath, mock_isfile, mock_exists, mock_run):
        """Test handling of invalid JSON output."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_abspath.side_effect = lambda x: x

        mock_process = MagicMock()
        mock_process.stdout = "Invalid JSON"
        mock_run.return_value = mock_process

        result = ts_analyze_code("test.ts")

        assert not result.is_success
        assert "Failed to parse JSON output" in result.error

    @patch("pipe.core.tools.ts_analyze_code.get_project_root")
    @patch("pipe.core.tools.ts_analyze_code.os.path.exists")
    @patch("pipe.core.tools.ts_analyze_code.os.path.isfile")
    @patch("pipe.core.tools.ts_analyze_code.os.path.abspath")
    def test_unexpected_error(self, mock_abspath, mock_isfile, mock_exists, mock_root):
        """Test handling of unexpected exceptions."""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_abspath.side_effect = lambda x: x
        # Mock get_project_root to raise an exception inside the try block
        mock_root.side_effect = Exception("Unexpected error")

        result = ts_analyze_code("test.ts")

        assert not result.is_success
        assert "An unexpected error occurred" in result.error
        assert "Unexpected error" in result.error


class TestParseFileResult:
    """Tests for _parse_file_result internal function."""

    def test_parse_full_result(self):
        """Test parsing a complete file analysis result with all fields."""
        data = {
            "file_path": "test.ts",
            "imports": [
                {
                    "module": "fs",
                    "named_imports": ["readFileSync"],
                    "default_import": "fsDefault",
                    "namespace_import": "fsNamespace",
                    "lineno": 1,
                }
            ],
            "exports": [
                {
                    "module": "./other",
                    "named_exports": ["MyClass"],
                    "lineno": 5,
                    "is_re_export": True,
                }
            ],
            "classes": [
                {
                    "name": "MyClass",
                    "lineno": 10,
                    "end_lineno": 20,
                    "is_exported": True,
                    "is_default_export": True,
                    "base_classes": ["BaseClass"],
                    "properties": [
                        {
                            "name": "prop",
                            "lineno": 11,
                            "end_lineno": 11,
                            "type_hint": "string",
                            "is_static": True,
                            "is_readonly": True,
                            "is_optional": True,
                        }
                    ],
                    "methods": [
                        {
                            "name": "method",
                            "lineno": 13,
                            "end_lineno": 15,
                            "signature": "method(x: number): void",
                            "parameters": ["x"],
                            "return_type": "void",
                            "is_static": True,
                            "is_async": True,
                        }
                    ],
                }
            ],
            "interfaces": [
                {
                    "name": "MyInterface",
                    "lineno": 25,
                    "end_lineno": 30,
                    "is_exported": True,
                    "is_default_export": False,
                    "extends": ["OtherInterface"],
                    "properties": [
                        {
                            "name": "iProp",
                            "lineno": 26,
                            "end_lineno": 26,
                            "type_hint": "number",
                            "is_optional": True,
                        }
                    ],
                }
            ],
            "type_aliases": [
                {
                    "name": "MyType",
                    "lineno": 35,
                    "end_lineno": 35,
                    "is_exported": True,
                    "is_default_export": False,
                    "definition": "string | number",
                }
            ],
            "functions": [
                {
                    "name": "myFunc",
                    "lineno": 40,
                    "end_lineno": 45,
                    "is_exported": True,
                    "is_default_export": False,
                    "signature": "myFunc(y: string): string",
                    "parameters": ["y"],
                    "return_type": "string",
                    "is_async": True,
                }
            ],
            "variables": [
                {
                    "name": "myVar",
                    "lineno": 50,
                    "end_lineno": 50,
                    "type_hint": "boolean",
                    "is_exported": True,
                    "declaration_type": "const",
                    "is_arrow_function": True,
                    "parameters": ["z"],
                    "return_type": "boolean",
                }
            ],
        }

        result = _parse_file_result(data)

        assert isinstance(result, FileAnalysisResult)
        assert result.file_path == "test.ts"

        assert len(result.imports) == 1
        assert result.imports[0].module == "fs"
        assert result.imports[0].default_import == "fsDefault"
        assert result.imports[0].namespace_import == "fsNamespace"

        assert len(result.exports) == 1
        assert result.exports[0].module == "./other"
        assert result.exports[0].is_re_export is True

        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "MyClass"
        assert cls.is_default_export is True
        assert cls.base_classes == ["BaseClass"]
        assert cls.properties[0].is_static is True
        assert cls.properties[0].is_readonly is True
        assert cls.properties[0].is_optional is True
        assert cls.methods[0].is_static is True
        assert cls.methods[0].is_async is True
        assert cls.methods[0].parameters == ["x"]

        assert len(result.interfaces) == 1
        iface = result.interfaces[0]
        assert iface.name == "MyInterface"
        assert iface.extends == ["OtherInterface"]
        assert iface.properties[0].is_optional is True

        assert len(result.type_aliases) == 1
        assert result.type_aliases[0].is_exported is True

        assert len(result.functions) == 1
        func = result.functions[0]
        assert func.is_async is True
        assert func.parameters == ["y"]

        assert len(result.variables) == 1
        var = result.variables[0]
        assert var.declaration_type == "const"
        assert var.is_arrow_function is True
        assert var.parameters == ["z"]
        assert var.return_type == "boolean"

    def test_parse_minimal_result(self):
        """Test parsing a minimal file analysis result with missing optional fields."""
        data = {"file_path": "minimal.ts"}
        result = _parse_file_result(data)

        assert result.file_path == "minimal.ts"
        assert result.imports == []
        assert result.classes == []
        assert result.functions == []
