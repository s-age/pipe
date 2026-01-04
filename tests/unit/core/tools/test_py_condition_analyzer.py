import ast
from unittest.mock import MagicMock, patch

from pipe.core.tools.py_condition_analyzer import (
    ConditionType,
    FunctionVisitor,
    _ast_unparse_safe,
    _is_builtin,
    _is_stdlib_call,
    py_condition_analyzer,
)


class TestIsBuiltin:
    """Tests for _is_builtin helper function."""

    def test_builtin_names(self):
        """Test that common builtins are correctly identified."""
        assert _is_builtin("print") is True
        assert _is_builtin("len") is True
        assert _is_builtin("dict") is True
        assert _is_builtin("Exception") is True

    def test_non_builtin_names(self):
        """Test that non-builtin names return False."""
        assert _is_builtin("my_custom_function") is False
        assert _is_builtin("repo") is False


class TestIsStdlibCall:
    """Tests for _is_stdlib_call helper function."""

    def test_stdlib_modules(self):
        """Test calls from standard library modules."""
        assert _is_stdlib_call("os.path.join") is True
        assert _is_stdlib_call("json.dumps") is True
        assert _is_stdlib_call("re.search") is True
        assert _is_stdlib_call("datetime.datetime.now") is True

    def test_stdlib_classes(self):
        """Test direct usage of standard library classes."""
        assert _is_stdlib_call("Path") is True
        assert _is_stdlib_call("Path.exists") is True
        assert _is_stdlib_call("Decimal") is True

    def test_non_stdlib_calls(self):
        """Test calls from non-standard library modules."""
        assert _is_stdlib_call("pipe.core.utils.path.join") is False
        assert _is_stdlib_call("my_module.func") is False
        assert _is_stdlib_call("local_func") is False


class TestAstUnparseSafe:
    """Tests for _ast_unparse_safe helper function."""

    def test_valid_node(self):
        """Test unparsing a valid AST node."""
        expr = ast.parse("x + 1").body[0]
        assert isinstance(expr, ast.Expr)
        node = expr.value
        assert _ast_unparse_safe(node) == "x + 1"

    def test_invalid_node(self):
        """Test handling of invalid nodes or errors during unparsing."""
        # Passing something that isn't an AST node
        assert _ast_unparse_safe(None) is None  # type: ignore


class TestFunctionVisitor:
    """Tests for FunctionVisitor class."""

    def test_visit_if_elif_else(self):
        """Test analyzing if-elif-else structure."""
        code = """
if x > 0:
    pass
elif x < 0:
    pass
else:
    pass
"""
        tree = ast.parse(code)
        visitor = FunctionVisitor()
        for node in tree.body:
            visitor.visit(node)

        assert len(visitor.branches) == 3
        assert visitor.branches[0].type == ConditionType.IF
        assert visitor.branches[0].condition_code == "x > 0"
        assert visitor.branches[1].type == ConditionType.ELIF
        assert visitor.branches[1].condition_code == "x < 0"
        assert visitor.branches[2].type == ConditionType.ELSE
        assert visitor.branches[2].condition_code is None
        assert visitor.complexity == 3

    def test_visit_loops(self):
        """Test analyzing for and while loops."""
        code = """
for i in range(10):
    pass
while True:
    pass
"""
        tree = ast.parse(code)
        visitor = FunctionVisitor()
        for node in tree.body:
            visitor.visit(node)

        assert len(visitor.branches) == 2
        assert visitor.branches[0].type == ConditionType.FOR
        assert visitor.branches[0].condition_code == "in range(10)"
        assert visitor.branches[1].type == ConditionType.WHILE
        assert visitor.branches[1].condition_code == "True"
        assert visitor.complexity == 3

    def test_visit_async_for(self):
        """Test analyzing async for loops."""
        code = """
async def func():
    async for i in range(10):
        pass
"""
        tree = ast.parse(code)
        # Get the AsyncFor node inside the function
        async_for_node = tree.body[0].body[0]  # type: ignore
        visitor = FunctionVisitor()
        visitor.visit(async_for_node)

        assert len(visitor.branches) == 1
        assert visitor.branches[0].type == ConditionType.FOR
        assert visitor.branches[0].condition_code == "in range(10)"
        assert visitor.complexity == 2

    def test_visit_try_except(self):
        """Test analyzing try-except blocks."""
        code = """
try:
    do_something()
except ValueError:
    handle_error()
except Exception as e:
    log_error(e)
"""
        tree = ast.parse(code)
        visitor = FunctionVisitor()
        for node in tree.body:
            visitor.visit(node)

        # TRY + 2 EXCEPTs
        assert len(visitor.branches) == 3
        assert visitor.branches[0].type == ConditionType.TRY
        assert visitor.branches[1].type == ConditionType.EXCEPT
        assert visitor.branches[1].condition_code == "ValueError"
        assert visitor.branches[2].type == ConditionType.EXCEPT
        assert visitor.branches[2].condition_code == "Exception"
        assert visitor.complexity == 3

    def test_visit_match_case(self):
        """Test analyzing match-case blocks (Python 3.10+)."""
        code = """
match value:
    case 1:
        pass
    case 2 | 3:
        pass
    case _:
        pass
"""
        tree = ast.parse(code)
        visitor = FunctionVisitor()
        for node in tree.body:
            visitor.visit(node)

        assert len(visitor.branches) == 4
        assert visitor.branches[0].type == ConditionType.MATCH
        assert visitor.branches[0].condition_code == "value"
        assert visitor.branches[1].type == ConditionType.CASE
        assert visitor.branches[1].condition_code == "1"
        assert visitor.branches[2].type == ConditionType.CASE
        assert visitor.branches[2].condition_code == "2 | 3"
        assert visitor.branches[3].type == ConditionType.CASE
        assert visitor.branches[3].condition_code == "_"
        assert visitor.complexity == 4

    def test_visit_call_mock_candidates(self):
        """Test identifying mock candidates from function calls."""
        code = """
self.repo.save(data)
other_func()
print("hello")
os.path.join("a", "b")
self.helper_method()
"""
        tree = ast.parse(code)
        visitor = FunctionVisitor()
        for node in tree.body:
            visitor.visit(node)

        # Candidates should be: self.repo.save, other_func, self.helper_method
        # print is builtin, os.path.join is stdlib
        names = [c.name for c in visitor.mock_candidates]
        assert "self.repo.save" in names
        assert "other_func" in names
        assert "self.helper_method" in names
        assert "print" not in names
        assert "os.path.join" not in names

        # Check is_attribute_call
        for candidate in visitor.mock_candidates:
            if candidate.name == "self.repo.save":
                assert candidate.is_attribute_call is True
            if candidate.name == "other_func":
                assert candidate.is_attribute_call is False


class TestPyConditionAnalyzer:
    """Tests for the main py_condition_analyzer tool."""

    @patch("pipe.core.tools.py_condition_analyzer.FileRepositoryFactory.create")
    def test_successful_analysis(self, mock_repo_factory):
        """Test successful analysis of a Python file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True

        source_code = """
def my_function(a, b=1, *args, **kwargs):
    if a > 0:
        return True
    return False

class MyClass:
    def method(self, x):
        for i in range(x):
            print(i)
"""
        mock_repo.read_text.return_value = source_code

        result = py_condition_analyzer("test.py")

        assert result.is_success
        assert result.data is not None
        assert len(result.data.functions) == 2

        # Check my_function
        func1 = next(f for f in result.data.functions if f.name == "my_function")
        assert "a" in func1.args
        assert "b" in func1.args
        assert "*args" in func1.args
        assert "**kwargs" in func1.args
        assert len(func1.branches) == 1
        assert func1.branches[0].type == ConditionType.IF

        # Check method
        func2 = next(f for f in result.data.functions if f.name == "method")
        assert "self" in func2.args
        assert "x" in func2.args
        assert len(func2.branches) == 1
        assert func2.branches[0].type == ConditionType.FOR

    @patch("pipe.core.tools.py_condition_analyzer.FileRepositoryFactory.create")
    def test_filter_by_function_name(self, mock_repo_factory):
        """Test filtering analysis by function name."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True

        source_code = "def func1(): pass\ndef func2(): pass"
        mock_repo.read_text.return_value = source_code

        result = py_condition_analyzer("test.py", function_name="func1")

        assert result.is_success
        assert result.data is not None
        assert len(result.data.functions) == 1
        assert result.data.functions[0].name == "func1"

    @patch("pipe.core.tools.py_condition_analyzer.FileRepositoryFactory.create")
    def test_file_not_found(self, mock_repo_factory):
        """Test error when file does not exist."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = False

        result = py_condition_analyzer("nonexistent.py")

        assert not result.is_success
        assert "File not found" in result.error

    @patch("pipe.core.tools.py_condition_analyzer.FileRepositoryFactory.create")
    def test_not_a_python_file(self, mock_repo_factory):
        """Test error when file is not a Python file."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True

        result = py_condition_analyzer("test.txt")

        assert not result.is_success
        assert "Not a Python file" in result.error

    @patch("pipe.core.tools.py_condition_analyzer.FileRepositoryFactory.create")
    def test_syntax_error(self, mock_repo_factory):
        """Test error when file has syntax errors."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = "def invalid syntax"

        result = py_condition_analyzer("test.py")

        assert not result.is_success
        assert "Syntax error" in result.error

    @patch("pipe.core.tools.py_condition_analyzer.FileRepositoryFactory.create")
    def test_function_not_found(self, mock_repo_factory):
        """Test error when specified function is not found."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.return_value = True
        mock_repo.read_text.return_value = "def func1(): pass"

        result = py_condition_analyzer("test.py", function_name="nonexistent")

        assert not result.is_success
        assert "Function 'nonexistent' not found" in result.error

    @patch("pipe.core.tools.py_condition_analyzer.FileRepositoryFactory.create")
    def test_general_exception(self, mock_repo_factory):
        """Test handling of general exceptions during analysis."""
        mock_repo = MagicMock()
        mock_repo_factory.return_value = mock_repo
        mock_repo.exists.side_effect = Exception("Unexpected error")

        result = py_condition_analyzer("test.py")

        assert not result.is_success
        assert "Analysis failed: Unexpected error" in result.error
