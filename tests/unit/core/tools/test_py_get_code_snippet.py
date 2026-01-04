from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_get_code_snippet import CodeSnippetResult, py_get_code_snippet


class TestPyGetCodeSnippet:
    """Unit tests for py_get_code_snippet tool."""

    @pytest.fixture
    def mock_repo(self):
        """Fixture for mocked FileRepository."""
        repo = MagicMock()
        repo.exists.return_value = True
        repo.is_file.return_value = True
        return repo

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_successful_function_extraction(self, mock_create, mock_repo):
        """Test extracting a function snippet successfully."""
        mock_create.return_value = mock_repo
        content = "def hello():\n    print('hello')\n"
        mock_repo.read_text.return_value = content

        result = py_get_code_snippet("test.py", "hello")

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, CodeSnippetResult)
        assert result.data.snippet == content
        mock_repo.exists.assert_called_once_with("test.py")
        mock_repo.read_text.assert_called_once_with("test.py")

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_successful_class_extraction(self, mock_create, mock_repo):
        """Test extracting a class snippet successfully."""
        mock_create.return_value = mock_repo
        content = "class MyClass:\n    def method(self):\n        pass\n"
        mock_repo.read_text.return_value = content

        result = py_get_code_snippet("test.py", "MyClass")

        assert result.is_success
        assert result.data.snippet == content

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_successful_variable_extraction(self, mock_create, mock_repo):
        """Test extracting a variable assignment snippet successfully."""
        mock_create.return_value = mock_repo
        content = "MY_VAR = 123\n"
        mock_repo.read_text.return_value = content

        result = py_get_code_snippet("test.py", "MY_VAR")

        assert result.is_success
        assert result.data.snippet == content

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_file_not_found(self, mock_create, mock_repo):
        """Test handling when file is not found."""
        mock_create.return_value = mock_repo
        mock_repo.exists.return_value = False

        result = py_get_code_snippet("missing.py", "any")

        assert not result.is_success
        assert "File not found" in result.error

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_path_is_not_a_file(self, mock_create, mock_repo):
        """Test handling when path is a directory."""
        mock_create.return_value = mock_repo
        mock_repo.is_file.return_value = False

        result = py_get_code_snippet("dir/", "any")

        assert not result.is_success
        assert "Path is not a file" in result.error

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_symbol_not_found(self, mock_create, mock_repo):
        """Test handling when symbol is not found in file."""
        mock_create.return_value = mock_repo
        content = "def other():\n    pass\n"
        mock_repo.read_text.return_value = content

        result = py_get_code_snippet("test.py", "missing_func")

        assert not result.is_success
        assert "Symbol 'missing_func' not found" in result.error

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_unicode_decode_error(self, mock_create, mock_repo):
        """Test handling of binary files (UnicodeDecodeError)."""
        mock_create.return_value = mock_repo
        mock_repo.read_text.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "reason"
        )

        result = py_get_code_snippet("binary.bin", "any")

        assert not result.is_success
        assert "Cannot decode file" in result.error

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_value_error(self, mock_create, mock_repo):
        """Test handling of ValueError."""
        mock_create.return_value = mock_repo
        mock_repo.read_text.side_effect = ValueError("Invalid path")

        result = py_get_code_snippet("invalid", "any")

        assert not result.is_success
        assert "Invalid file path" in result.error

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_general_exception(self, mock_create, mock_repo):
        """Test handling of unexpected exceptions."""
        mock_create.return_value = mock_repo
        mock_repo.read_text.side_effect = Exception("Unexpected")

        result = py_get_code_snippet("test.py", "any")

        assert not result.is_success
        assert "Failed to extract code snippet" in result.error

    @patch("pipe.core.tools.py_get_code_snippet.FileRepositoryFactory.create")
    def test_syntax_error_in_file(self, mock_create, mock_repo):
        """Test handling of syntax errors in the target file."""
        mock_create.return_value = mock_repo
        mock_repo.read_text.return_value = "invalid python code ("

        result = py_get_code_snippet("bad.py", "any")

        assert not result.is_success
        assert "Failed to extract code snippet" in result.error
