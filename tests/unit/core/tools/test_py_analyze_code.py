import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_analyze_code import (
    _analyze_single_file,
    _ast_unparse_safe,
    _extract_class_info,
    _extract_method_info,
    py_analyze_code,
)


class TestAstUnparseSafe:
    """Tests for _ast_unparse_safe function."""

    def test_valid_node(self):
        """Test unparsing a valid AST node."""
        node = ast.parse("x: int = 1").body[0]
        result = _ast_unparse_safe(node)
        assert result == "x: int = 1"

    def test_invalid_node_exception(self):
        """Test handling of exception during unparse."""
        with patch("ast.unparse", side_effect=Exception("Unparse error")):
            result = _ast_unparse_safe(MagicMock())
            assert result is None


class TestExtractMethodInfo:
    """Tests for _extract_method_info function."""

    def test_regular_function(self):
        """Test extracting info from a regular function."""
        code = 'def func(a, b: int, *args, **kwargs) -> str:\n    """Doc."""\n    return "hi"'
        node = ast.parse(code).body[0]
        assert isinstance(node, ast.FunctionDef)
        info = _extract_method_info(node)

        assert info.name == "func"
        assert info.docstring == "Doc."
        assert info.return_type == "str"
        assert "a" in info.parameters
        assert "b: int" in info.parameters
        assert "*args" in info.parameters
        assert "**kwargs" in info.parameters
        assert info.signature == "func(a, b: int, *args, **kwargs) -> str"

    def test_async_function(self):
        """Test extracting info from an async function."""
        code = "async def async_func(): pass"
        node = ast.parse(code).body[0]
        assert isinstance(node, ast.AsyncFunctionDef)
        info = _extract_method_info(node)

        assert info.name == "async_func"
        assert info.signature == "async_func()"

    def test_function_with_annotated_args_kwargs(self):
        """Test extracting info from a function with annotated *args and **kwargs."""
        code = "def func(*args: int, **kwargs: str): pass"
        node = ast.parse(code).body[0]
        assert isinstance(node, ast.FunctionDef)
        info = _extract_method_info(node)

        assert "*args: int" in info.parameters
        assert "**kwargs: str" in info.parameters

    def test_function_with_complex_types(self):
        """Test extracting info from a function with complex type hints."""
        code = "def func(a: list[int] | None) -> dict[str, Any]: pass"
        node = ast.parse(code).body[0]
        assert isinstance(node, ast.FunctionDef)
        info = _extract_method_info(node)

        assert "a: list[int] | None" in info.parameters
        assert info.return_type == "dict[str, Any]"


class TestExtractClassInfo:
    """Tests for _extract_class_info function."""

    def test_complex_class(self):
        """Test extracting info from a class with various members."""
        code = """
class MyClass(Base1, Base2):
    \"\"\"Class doc.\"\"\"
    attr: int = 1

    def __init__(self, x):
        self.x = x

    @property
    def my_prop(self) -> str:
        return "prop"

    async def my_method(self, y: float):
        pass
"""
        node = ast.parse(code).body[0]
        assert isinstance(node, ast.ClassDef)
        info = _extract_class_info(node)

        assert info.name == "MyClass"
        assert info.docstring == "Class doc."
        assert info.base_classes == ["Base1", "Base2"]

        # Properties
        assert len(info.properties) == 2
        attr_prop = next(p for p in info.properties if p.name == "attr")
        assert attr_prop.type_hint == "int"
        assert attr_prop.is_property_decorator is False

        prop_decorator = next(p for p in info.properties if p.name == "my_prop")
        assert prop_decorator.type_hint == "str"
        assert prop_decorator.is_property_decorator is True

        # Methods
        assert len(info.methods) == 2
        init_method = next(m for m in info.methods if m.name == "__init__")
        assert init_method.signature == "__init__(self, x)"

        async_method = next(m for m in info.methods if m.name == "my_method")
        assert async_method.name == "my_method"
        assert "y: float" in async_method.parameters


class TestAnalyzeSingleFile:
    """Tests for _analyze_single_file function."""

    def test_valid_file(self):
        """Test analyzing a valid Python file."""
        code = """
VAR = 123
def func(): pass
class MyClass: pass
"""
        result = _analyze_single_file("test.py", code)
        assert result is not None
        assert result.file_path == "test.py"
        assert len(result.variables) == 1
        assert result.variables[0].name == "VAR"
        assert len(result.functions) == 1
        assert result.functions[0].name == "func"
        assert len(result.classes) == 1
        assert result.classes[0].name == "MyClass"

    def test_syntax_error(self):
        """Test handling of syntax error in file."""
        code = "if True"
        result = _analyze_single_file("error.py", code)
        assert result is None


class TestPyAnalyzeCode:
    """Tests for py_analyze_code tool."""

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    def test_analyze_single_file_success(self, mock_repo_factory):
        """Test successful analysis of a single file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.return_value = "def hello(): pass"

        result = py_analyze_code("hello.py")

        assert isinstance(result, ToolResult)
        assert result.is_success
        assert result.data is not None
        assert result.data.total_files == 1
        assert len(result.data.files) == 1
        assert result.data.files[0].file_path == "hello.py"
        assert result.data.functions[0].name == "hello"

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    @patch("pathlib.Path.glob")
    def test_analyze_directory_success(self, mock_glob, mock_repo_factory):
        """Test successful analysis of a directory."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = False

        mock_glob.return_value = [Path("dir/file1.py"), Path("dir/file2.py")]

        mock_repo.read_text.side_effect = ["class A: pass", "def b(): pass"]

        result = py_analyze_code("dir")

        assert result.is_success
        assert result.data.total_files == 2
        assert len(result.data.files) == 2
        # Check backward compatibility fields
        assert any(c.name == "A" for c in result.data.classes)
        assert any(f.name == "b" for f in result.data.functions)

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    def test_path_not_found(self, mock_repo_factory):
        """Test handling of non-existent path."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = False

        result = py_analyze_code("nonexistent")
        assert not result.is_success
        assert "Path not found" in result.error

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    def test_not_python_file(self, mock_repo_factory):
        """Test handling of non-Python file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True

        result = py_analyze_code("data.txt")
        assert not result.is_success
        assert "Not a Python file" in result.error

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    @patch("pathlib.Path.glob")
    def test_too_many_files(self, mock_glob, mock_repo_factory):
        """Test handling of too many files in directory."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = False

        mock_glob.return_value = [Path(f"file{i}.py") for i in range(10)]

        result = py_analyze_code("dir", max_files=5)
        assert not result.is_success
        assert "Too many files" in result.error

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    @patch("pathlib.Path.glob")
    def test_no_python_files_in_directory(self, mock_glob, mock_repo_factory):
        """Test handling of directory with no Python files."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = False
        mock_glob.return_value = []

        result = py_analyze_code("empty_dir")
        assert not result.is_success
        assert "No Python files found" in result.error

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    def test_unicode_decode_error(self, mock_repo_factory):
        """Test skipping files with UnicodeDecodeError."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "reason"
        )

        result = py_analyze_code("binary.py")
        assert not result.is_success
        assert "No valid Python files could be analyzed" in result.error

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    def test_general_exception_during_read(self, mock_repo_factory):
        """Test skipping files with general exception during read."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = True
        mock_repo.read_text.side_effect = Exception("Read error")

        result = py_analyze_code("error.py")
        assert not result.is_success
        assert "No valid Python files could be analyzed" in result.error

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    @patch("pathlib.Path.glob")
    def test_glob_exception(self, mock_glob, mock_repo_factory):
        """Test handling of exception during glob."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.is_file.return_value = False
        mock_glob.side_effect = Exception("Glob error")

        result = py_analyze_code("dir")
        assert not result.is_success
        assert "Failed to list directory" in result.error

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    def test_general_exception(self, mock_repo_factory):
        """Test handling of general exception in py_analyze_code."""
        mock_repo_factory.side_effect = Exception("Unexpected error")
        result = py_analyze_code("any.py")
        assert not result.is_success
        assert "Failed to analyze code" in result.error

    @patch("pipe.core.tools.py_analyze_code.FileRepositoryFactory.create")
    def test_value_error_handling(self, mock_repo_factory):
        """Test that ValueError is caught and returned as an error."""
        mock_repo_factory.side_effect = ValueError("Invalid path configuration")
        result = py_analyze_code("any_path")
        assert not result.is_success
        assert "Invalid path: Invalid path configuration" in result.error
