"""Unit tests for py_get_type_hints tool."""

from unittest.mock import MagicMock, mock_open, patch

from pipe.core.tools.py_get_type_hints import py_get_type_hints


class TestPyGetTypeHints:
    """Test suite for py_get_type_hints function."""

    @patch("pipe.core.tools.py_get_type_hints.os.path.exists")
    def test_file_not_found(self, mock_exists: MagicMock) -> None:
        """Test behavior when the file does not exist."""
        mock_exists.return_value = False  # type: ignore[attr-defined]

        result = py_get_type_hints("non_existent.py", "some_func")

        assert result.is_success is False
        assert result.error == "File not found: non_existent.py"

    @patch("pipe.core.tools.py_get_type_hints.os.path.exists")
    def test_function_type_hints(self, mock_exists: MagicMock) -> None:
        """Test extracting type hints from a function definition."""
        mock_exists.return_value = True  # type: ignore[attr-defined]
        source_code = "def my_func(a: int, b: str = 'default') -> bool: pass"

        with patch("builtins.open", mock_open(read_data=source_code)):
            result = py_get_type_hints("test.py", "my_func")

            assert result.is_success is True
            assert result.data is not None
            assert result.data["type_hints"] == {
                "a": "int",
                "b": "str",
                "return": "bool",
            }

    @patch("pipe.core.tools.py_get_type_hints.os.path.exists")
    def test_class_type_hints(self, mock_exists: MagicMock) -> None:
        """Test extracting type hints from a class definition."""
        mock_exists.return_value = True  # type: ignore[attr-defined]
        source_code = (
            "class MyClass:\n"
            "    x: int\n"
            "    y: str = 'hello'\n"
            "    def method(self): pass"
        )

        with patch("builtins.open", mock_open(read_data=source_code)):
            result = py_get_type_hints("test.py", "MyClass")

            assert result.is_success is True
            assert result.data is not None
            assert result.data["type_hints"] == {"x": "int", "y": "str"}

    @patch("pipe.core.tools.py_get_type_hints.os.path.exists")
    def test_symbol_not_found(self, mock_exists: MagicMock) -> None:
        """Test behavior when the symbol is not found in the file."""
        mock_exists.return_value = True  # type: ignore[attr-defined]
        source_code = "x = 1\ndef other_func(): pass"

        with patch("builtins.open", mock_open(read_data=source_code)):
            result = py_get_type_hints("test.py", "missing_symbol")

            assert result.is_success is False
            assert result.error is not None
            assert "not found" in result.error

    @patch("pipe.core.tools.py_get_type_hints.os.path.exists")
    def test_no_type_hints(self, mock_exists: MagicMock) -> None:
        """Test behavior when the symbol exists but has no type hints."""
        mock_exists.return_value = True  # type: ignore[attr-defined]
        source_code = "def no_hints(a, b): pass"

        with patch("builtins.open", mock_open(read_data=source_code)):
            result = py_get_type_hints("test.py", "no_hints")

            assert result.is_success is False
            assert result.error is not None
            assert "not found" in result.error

    @patch("pipe.core.tools.py_get_type_hints.os.path.exists")
    def test_complex_type_hints(self, mock_exists: MagicMock) -> None:
        """Test extracting complex type hints (List, Optional, Union)."""
        mock_exists.return_value = True  # type: ignore[attr-defined]
        source_code = (
            "from typing import List, Optional, Union\n"
            "def complex_func(a: List[str], b: Optional[int] | None = None) -> Union[str, int]: pass"
        )

        with patch("builtins.open", mock_open(read_data=source_code)):
            result = py_get_type_hints("test.py", "complex_func")

            assert result.is_success is True
            assert result.data is not None
            hints = result.data["type_hints"]
            # ast.unparse might vary slightly, but should be equivalent
            assert "List[str]" in hints["a"]
            assert "Optional[int] | None" in hints["b"]
            assert "Union[str, int]" in hints["return"]

    @patch("pipe.core.tools.py_get_type_hints.os.path.exists")
    def test_class_non_name_annotation(self, mock_exists: MagicMock) -> None:
        """Test that non-Name targets in class annotations are ignored."""
        mock_exists.return_value = True  # type: ignore[attr-defined]
        source_code = "class MyClass:\n    x: int\n    a.b: str = 'val'\n"

        with patch("builtins.open", mock_open(read_data=source_code)):
            result = py_get_type_hints("test.py", "MyClass")

            assert result.is_success is True
            assert result.data is not None
            assert result.data["type_hints"] == {"x": "int"}
            assert "b" not in result.data["type_hints"]

    @patch("pipe.core.tools.py_get_type_hints.os.path.exists")
    def test_function_partial_annotations(self, mock_exists: MagicMock) -> None:
        """Test function where only some arguments are annotated."""
        mock_exists.return_value = True  # type: ignore[attr-defined]
        source_code = "def partial_func(a: int, b, c: str): pass"

        with patch("builtins.open", mock_open(read_data=source_code)):
            result = py_get_type_hints("test.py", "partial_func")

            assert result.is_success is True
            assert result.data is not None
            assert result.data["type_hints"] == {"a": "int", "c": "str"}
            assert "b" not in result.data["type_hints"]
            assert "return" not in result.data["type_hints"]
