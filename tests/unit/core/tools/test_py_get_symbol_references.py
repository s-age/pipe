"""Unit tests for py_get_symbol_references tool."""

from unittest.mock import MagicMock, mock_open, patch

from pipe.core.tools.py_get_symbol_references import py_get_symbol_references


class TestPyGetSymbolReferences:
    """Unit tests for py_get_symbol_references tool."""

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    def test_file_not_found(self, mock_exists: MagicMock) -> None:
        """Test when the source file does not exist."""
        mock_exists.return_value = False
        result = py_get_symbol_references("non_existent.py", "my_symbol")
        assert result.is_success is False
        assert result.error is not None
        assert "File not found" in result.error

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.isdir")
    def test_search_directory_not_found(
        self, mock_isdir: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test when the search directory does not exist."""
        mock_exists.return_value = True
        mock_isdir.return_value = False
        result = py_get_symbol_references(
            "source.py", "my_symbol", search_directory="invalid_dir"
        )
        assert result.is_success is False
        assert result.error is not None
        assert "Search directory not found" in result.error

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="invalid code")
    @patch("pipe.core.tools.py_get_symbol_references.ast.parse")
    def test_syntax_error(
        self, mock_parse: MagicMock, mock_file: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test when the source file has a syntax error."""
        mock_exists.return_value = True
        mock_parse.side_effect = SyntaxError("invalid syntax")

        result = py_get_symbol_references("source.py", "my_symbol")
        assert result.is_success is False
        assert result.error is not None
        assert "Syntax error" in result.error

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="def other(): pass")
    def test_symbol_not_found(
        self, mock_file: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test when the symbol is not found in the source file."""
        mock_exists.return_value = True
        result = py_get_symbol_references("source.py", "my_symbol")
        assert result.is_success is False
        assert result.error is not None
        assert "Symbol 'my_symbol' not found" in result.error

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.isdir")
    @patch("pipe.core.tools.py_get_symbol_references.get_project_root")
    @patch("pipe.core.tools.py_get_symbol_references.os.walk")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.abspath")
    @patch("builtins.open")
    def test_successful_search(
        self,
        mock_file: MagicMock,
        mock_abspath: MagicMock,
        mock_walk: MagicMock,
        mock_root: MagicMock,
        mock_isdir: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        """Test successful symbol reference search."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_root.return_value = "/project"
        mock_abspath.side_effect = lambda x: x

        # Source file content
        source_code = "def my_symbol(): pass\n"

        # Mocking open for multiple files
        # 1. source.py (definition)
        # 2. ref1.py (reference)
        # 3. ref2.py (no reference)
        mock_file.side_effect = [
            mock_open(read_data=source_code).return_value,
            mock_open(read_data="my_symbol()\n").return_value,
            mock_open(read_data="other()\n").return_value,
        ]

        # Mocking os.walk
        mock_walk.return_value = [
            ("/project/src/pipe", ["subdir"], ["ref1.py", "ref2.py"]),
        ]

        result = py_get_symbol_references("source.py", "my_symbol")

        assert result.is_success is True
        assert result.data is not None
        assert result.data["symbol_name"] == "my_symbol"
        assert result.data["reference_count"] == 1
        assert result.data["references"][0]["file_path"] == "/project/src/pipe/ref1.py"
        assert result.data["references"][0]["lineno"] == 1
        assert result.data["references"][0]["line_content"] == "my_symbol()"

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.isdir")
    @patch("pipe.core.tools.py_get_symbol_references.os.walk")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.abspath")
    @patch("builtins.open")
    def test_skip_definition_range(
        self,
        mock_file: MagicMock,
        mock_abspath: MagicMock,
        mock_walk: MagicMock,
        mock_isdir: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        """Test that symbol definition lines are skipped in the original file."""
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_abspath.return_value = "/project/source.py"

        # Source file content: symbol spans lines 1-2
        source_code = "def my_symbol():\n    pass\nmy_symbol() # This is line 3\n"

        mock_file.side_effect = [
            mock_open(read_data=source_code).return_value,  # First read for definition
            mock_open(read_data=source_code).return_value,  # Second read for search
        ]

        mock_walk.return_value = [
            ("/project", [], ["source.py"]),
        ]

        result = py_get_symbol_references(
            "/project/source.py", "my_symbol", search_directory="/project"
        )

        assert result.is_success is True
        assert result.data is not None
        assert result.data["reference_count"] == 1
        assert result.data["references"][0]["lineno"] == 3

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.isdir")
    @patch("pipe.core.tools.py_get_symbol_references.os.walk")
    @patch("builtins.open")
    def test_handle_file_read_error(
        self,
        mock_file: MagicMock,
        mock_walk: MagicMock,
        mock_isdir: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        """Test that it continues if a file cannot be read."""
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_file.side_effect = [
            mock_open(read_data="def my_symbol(): pass").return_value,
            OSError("Permission denied"),
        ]

        mock_walk.return_value = [
            ("/project", [], ["unreadable.py"]),
        ]

        result = py_get_symbol_references(
            "source.py", "my_symbol", search_directory="/project"
        )

        assert result.is_success is True
        assert result.data is not None
        assert result.data["reference_count"] == 0

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.isdir")
    @patch("pipe.core.tools.py_get_symbol_references.os.walk")
    @patch("builtins.open")
    def test_handle_unicode_decode_error(
        self,
        mock_file: MagicMock,
        mock_walk: MagicMock,
        mock_isdir: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        """Test that it continues if a file has encoding issues."""
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_file.side_effect = [
            mock_open(read_data="def my_symbol(): pass").return_value,
            UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
        ]

        mock_walk.return_value = [
            ("/project", [], ["binary.py"]),
        ]

        result = py_get_symbol_references(
            "source.py", "my_symbol", search_directory="/project"
        )

        assert result.is_success is True
        assert result.data is not None
        assert result.data["reference_count"] == 0

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.isdir")
    @patch("pipe.core.tools.py_get_symbol_references.os.walk")
    @patch("builtins.open")
    def test_assignment_symbol(
        self,
        mock_file: MagicMock,
        mock_walk: MagicMock,
        mock_isdir: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        """Test finding a symbol defined by assignment."""
        mock_exists.return_value = True
        mock_isdir.return_value = True

        mock_file.side_effect = [
            mock_open(read_data="MY_CONST = 10").return_value,
            mock_open(read_data="print(MY_CONST)").return_value,
        ]

        mock_walk.return_value = [
            ("/project", [], ["ref.py"]),
        ]

        result = py_get_symbol_references(
            "source.py", "MY_CONST", search_directory="/project"
        )

        assert result.is_success is True
        assert result.data is not None
        assert result.data["reference_count"] == 1
        assert result.data["references"][0]["line_content"] == "print(MY_CONST)"

    @patch("pipe.core.tools.py_get_symbol_references.os.path.exists")
    @patch("pipe.core.tools.py_get_symbol_references.os.path.isdir")
    @patch("pipe.core.tools.py_get_symbol_references.os.walk")
    @patch("builtins.open")
    def test_skip_directories(
        self,
        mock_file: MagicMock,
        mock_walk: MagicMock,
        mock_isdir: MagicMock,
        mock_exists: MagicMock,
    ) -> None:
        """Test that non-source directories are skipped."""
        mock_exists.return_value = True
        mock_isdir.return_value = True

        dirs = ["__pycache__", "src"]
        mock_walk.return_value = [
            ("/project", dirs, []),
            ("/project/src", [], ["file.py"]),
        ]

        mock_file.side_effect = [
            mock_open(read_data="def my_symbol(): pass").return_value,
            mock_open(read_data="my_symbol()").return_value,
        ]

        result = py_get_symbol_references(
            "source.py", "my_symbol", search_directory="/project"
        )

        assert result.is_success is True
        assert result.data is not None
        # Verify that __pycache__ was removed from dirs list
        assert "__pycache__" not in dirs
        assert "src" in dirs
        assert result.data["reference_count"] == 1
