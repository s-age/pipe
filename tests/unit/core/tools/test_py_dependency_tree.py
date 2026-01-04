"""Unit tests for py_dependency_tree tool."""

import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.py_dependency_tree import (
    DependencyNode,
    DependencyTreeResult,
    _build_dependency_tree,
    _extract_function_calls,
    _get_decorator_name,
    _get_name_from_node,
    _resolve_import_path,
    format_dependency_tree,
    py_dependency_tree,
)


class TestPyDependencyTree:
    """Tests for py_dependency_tree function."""

    @patch("pipe.core.tools.py_dependency_tree.FileRepositoryFactory.create")
    def test_file_not_found(self, mock_repo_factory):
        """Test when the file does not exist."""
        mock_repo = MagicMock()
        mock_repo.exists.return_value = False
        mock_repo_factory.return_value = mock_repo

        result = py_dependency_tree("non_existent.py")

        assert isinstance(result, ToolResult)
        assert result.is_success is False
        assert "File not found" in result.error

    @patch("pipe.core.tools.py_dependency_tree.FileRepositoryFactory.create")
    def test_not_python_file(self, mock_repo_factory):
        """Test when the file is not a Python file."""
        mock_repo = MagicMock()
        mock_repo.exists.return_value = True
        mock_repo_factory.return_value = mock_repo

        result = py_dependency_tree("test.txt")

        assert result.is_success is False
        assert "Not a Python file" in result.error

    @patch("pipe.core.tools.py_dependency_tree.FileRepositoryFactory.create")
    @patch("pipe.core.tools.py_dependency_tree._build_dependency_tree")
    def test_success(self, mock_build, mock_repo_factory):
        """Test successful dependency tree building."""
        mock_repo = MagicMock()
        mock_repo.exists.return_value = True
        mock_repo_factory.return_value = mock_repo

        expected_data = DependencyTreeResult(file_path="test.py")
        mock_build.return_value = expected_data

        result = py_dependency_tree("test.py")

        assert result.is_success is True
        assert result.data == expected_data
        mock_build.assert_called_once()

    @patch("pipe.core.tools.py_dependency_tree.FileRepositoryFactory.create")
    def test_unexpected_error(self, mock_repo_factory):
        """Test handling of unexpected exceptions."""
        mock_repo_factory.side_effect = Exception("Unexpected error")

        result = py_dependency_tree("test.py")

        assert result.is_success is False
        assert "An unexpected error occurred" in result.error

    @patch("pipe.core.tools.py_dependency_tree.FileRepositoryFactory.create")
    def test_value_error(self, mock_repo_factory):
        """Test handling of ValueError (e.g. invalid path)."""
        mock_repo_factory.side_effect = ValueError("Invalid path")

        result = py_dependency_tree("test.py")

        assert result.is_success is False
        assert "Invalid path" in result.error


class TestBuildDependencyTree:
    """Tests for _build_dependency_tree internal function."""

    def test_circular_dependency(self):
        """Test detection of circular dependencies."""
        repo = MagicMock()
        file_path = "circular.py"
        abs_path = str(Path(file_path).resolve())
        visited = {abs_path}

        result = _build_dependency_tree(file_path, 3, visited, repo)

        assert result.circular is True
        assert result.file_path == file_path

    def test_max_depth_reached(self):
        """Test when maximum depth is reached."""
        repo = MagicMock()
        file_path = "depth.py"
        visited: set[str] = set()

        result = _build_dependency_tree(file_path, 2, visited, repo, current_depth=2)

        assert result.max_depth_reached is True
        assert result.file_path == file_path

    def test_basic_analysis(self):
        """Test analysis of a simple Python file."""
        repo = MagicMock()
        file_path = "simple.py"
        source = """
import os
from math import sqrt
@decorator
class MyClass(Base):
    def my_method(self):
        func_call()
@func_decorator
def my_func():
    another_call()
"""
        repo.read_text.return_value = source
        visited: set[str] = set()

        result = _build_dependency_tree(file_path, 3, visited, repo)

        assert result.file_path == file_path
        # Imports
        assert any(i.name == "os" for i in result.imports)
        assert any(i.name == "sqrt" and i.source == "math" for i in result.imports)
        # Classes
        assert any(c.name == "Base" for c in result.classes)
        # Functions (calls)
        assert any(f.name == "func_call" for f in result.functions)
        assert any(f.name == "another_call" for f in result.functions)
        # Decorators
        assert any(d.name == "decorator" for d in result.decorators)
        assert any(d.name == "func_decorator" for d in result.decorators)

    def test_syntax_error_handling(self):
        """Test that syntax errors in analyzed files are handled gracefully."""
        repo = MagicMock()
        repo.read_text.return_value = "invalid syntax ("
        visited: set[str] = set()

        result = _build_dependency_tree("invalid.py", 3, visited, repo)

        assert result.file_path == "invalid.py"
        assert not result.imports
        assert not result.classes

    @patch("pipe.core.tools.py_dependency_tree._resolve_import_path")
    def test_recursive_analysis(self, mock_resolve):
        """Test recursive analysis of local imports."""
        repo = MagicMock()
        repo.exists.side_effect = lambda p: p == "dep.py"
        repo.read_text.side_effect = lambda p: (
            "import sys" if p == "dep.py" else "from my_dep import dep"
        )

        mock_resolve.return_value = "dep.py"
        visited: set[str] = set()

        result = _build_dependency_tree("main.py", 3, visited, repo)

        assert any(
            i.name == "dep" and i.dependencies is not None for i in result.imports
        )
        dep_tree = next(i.dependencies for i in result.imports if i.name == "dep")
        assert dep_tree is not None
        assert any(i.name == "sys" for i in dep_tree.imports)

    def test_unexpected_exception_in_build(self):
        """Test handling of unexpected exceptions during build."""
        repo = MagicMock()
        repo.read_text.side_effect = Exception("Unexpected")
        visited: set[str] = set()

        # Should return result with what it has (empty)
        result = _build_dependency_tree("test.py", 3, visited, repo)
        assert result.file_path == "test.py"


class TestResolveImportPath:
    """Tests for _resolve_import_path function."""

    def test_resolve_direct_py(self, tmp_path):
        """Test resolving a direct .py file."""
        current_file = tmp_path / "main.py"
        dep_file = tmp_path / "dep.py"
        dep_file.touch()

        result = _resolve_import_path(str(current_file), "dep", 0)

        assert result == str(dep_file.resolve())

    def test_resolve_init_py(self, tmp_path):
        """Test resolving a package (__init__.py)."""
        current_file = tmp_path / "main.py"
        pkg_dir = tmp_path / "pkg"
        pkg_dir.mkdir()
        init_file = pkg_dir / "__init__.py"
        init_file.touch()

        result = _resolve_import_path(str(current_file), "pkg", 0)

        assert result == str(init_file.resolve())

    def test_resolve_relative(self, tmp_path):
        """Test resolving a relative import."""
        root = tmp_path
        other = root / "other.py"
        other.touch()

        pkg = root / "pkg"
        pkg.mkdir()
        (pkg / "__init__.py").touch()

        sub = pkg / "sub"
        sub.mkdir()
        (sub / "__init__.py").touch()

        current = sub / "module.py"
        current.touch()

        result = _resolve_import_path(str(current), "other", 2)

        assert result == str(other.resolve())

    def test_resolve_not_found(self, tmp_path):
        """Test when the import cannot be resolved."""
        current_file = tmp_path / "main.py"
        result = _resolve_import_path(str(current_file), "non_existent", 0)
        assert result is None


class TestExtractFunctionCalls:
    """Tests for _extract_function_calls function."""

    def test_extract_calls(self):
        """Test extracting various types of function calls."""
        source = """
def test_func():
    simple_call()
    obj.method_call()
    nested.obj.attr_call()
"""
        tree = ast.parse(source)
        func_def = tree.body[0]
        assert isinstance(func_def, ast.FunctionDef)

        calls = _extract_function_calls(func_def)

        assert "simple_call" in calls
        assert "obj.method_call" in calls
        assert "nested.obj.attr_call" in calls


class TestGetNameFromNode:
    """Tests for _get_name_from_node function."""

    def test_name_node(self):
        """Test extracting name from a Name node."""
        node = ast.Name(id="my_var", ctx=ast.Load())
        assert _get_name_from_node(node) == "my_var"

    def test_attribute_node(self):
        """Test extracting name from an Attribute node."""
        node = ast.Attribute(
            value=ast.Name(id="obj", ctx=ast.Load()), attr="attr", ctx=ast.Load()
        )
        assert _get_name_from_node(node) == "obj.attr"

    def test_attribute_no_value_name(self):
        """Test Attribute node where value is not a Name (e.g. Call)."""
        # func().attr
        node = ast.Attribute(
            value=ast.Call(
                func=ast.Name(id="func", ctx=ast.Load()), args=[], keywords=[]
            ),
            attr="attr",
            ctx=ast.Load(),
        )
        assert _get_name_from_node(node) == "attr"

    def test_unsupported_node(self):
        """Test with an unsupported node type."""
        node = ast.Constant(value=1)
        assert _get_name_from_node(node) is None


class TestGetDecoratorName:
    """Tests for _get_decorator_name function."""

    def test_decorator_name(self):
        """Test with a simple decorator name."""
        node = ast.Name(id="my_dec", ctx=ast.Load())
        assert _get_decorator_name(node) == "my_dec"

    def test_decorator_call(self):
        """Test with a decorator call (e.g., @dec())."""
        node = ast.Call(
            func=ast.Name(id="dec_factory", ctx=ast.Load()), args=[], keywords=[]
        )
        assert _get_decorator_name(node) == "dec_factory"

    def test_decorator_attribute(self):
        """Test with an attribute decorator (e.g., @obj.dec)."""
        node = ast.Attribute(
            value=ast.Name(id="obj", ctx=ast.Load()), attr="dec", ctx=ast.Load()
        )
        assert _get_decorator_name(node) == "obj.dec"

    def test_unsupported_decorator(self):
        """Test with an unsupported decorator node type."""
        node = ast.Constant(value=1)
        assert _get_decorator_name(node) is None


class TestFormatDependencyTree:
    """Tests for format_dependency_tree function."""

    def test_format_circular(self):
        """Test formatting a circular dependency."""
        tree = DependencyTreeResult(file_path="circular.py", circular=True)
        result = format_dependency_tree(tree)
        assert "circular.py" in result
        assert "[CIRCULAR DEPENDENCY DETECTED]" in result

    def test_format_max_depth(self):
        """Test formatting when max depth is reached."""
        tree = DependencyTreeResult(file_path="depth.py", max_depth_reached=True)
        result = format_dependency_tree(tree)
        assert "depth.py" in result
        assert "[Max depth reached]" in result

    def test_format_full_tree(self):
        """Test formatting a tree with all types of nodes."""
        tree = DependencyTreeResult(file_path="root.py")
        tree.imports.append(DependencyNode(name="os", source="import"))
        tree.classes.append(DependencyNode(name="MyClass", source="base_class"))
        tree.functions.append(DependencyNode(name="my_func", source="function_call"))
        tree.decorators.append(DependencyNode(name="my_dec", source="decorator"))

        result = format_dependency_tree(tree)

        assert "root.py" in result
        assert "Imports" in result
        assert "os (import)" in result
        assert "Classes" in result
        assert "MyClass (base_class)" in result
        assert "Functions" in result
        assert "my_func (function_call)" in result
        assert "Decorators" in result
        assert "my_dec (decorator)" in result

    def test_format_nested_tree(self):
        """Test formatting a tree with nested dependencies."""
        child_tree = DependencyTreeResult(file_path="child.py")
        child_tree.imports.append(DependencyNode(name="sys", source="import"))

        parent_tree = DependencyTreeResult(file_path="parent.py")
        parent_tree.imports.append(
            DependencyNode(name="child", source="local", dependencies=child_tree)
        )

        result = format_dependency_tree(parent_tree)

        assert "parent.py" in result
        assert "child (local)" in result
        # The first line of child_tree (child.py) is skipped in format_dependency_tree
        # but its content should be there.
        assert "sys (import)" in result

    def test_format_nested_classes_functions_decorators(self):
        """Test formatting nested dependencies for classes, functions, and decorators."""
        tree = DependencyTreeResult(file_path="root.py")

        child = DependencyTreeResult(file_path="child.py")
        child.functions.append(DependencyNode(name="sub", source="f"))

        tree.classes.append(DependencyNode(name="C", source="b", dependencies=child))
        tree.functions.append(DependencyNode(name="F", source="f", dependencies=child))
        tree.decorators.append(DependencyNode(name="D", source="d", dependencies=child))

        result = format_dependency_tree(tree)
        assert "sub (f)" in result
