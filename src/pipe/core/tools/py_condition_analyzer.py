import ast
import builtins
from enum import Enum

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.tool_result import ToolResult
from pydantic import BaseModel, Field


class ConditionType(str, Enum):
    IF = "if"
    ELIF = "elif"
    ELSE = "else"
    FOR = "for"
    WHILE = "while"
    TRY = "try"
    EXCEPT = "except"
    MATCH = "match"
    CASE = "case"


class MockCandidate(BaseModel):
    """Potential dependency to mock."""

    name: str = Field(..., description="Call name (e.g., self.repo.save)")
    lineno: int
    end_lineno: int | None = None
    is_attribute_call: bool = Field(..., description="True if it is a self.xxx call")


class BranchInfo(BaseModel):
    """Control flow branch information."""

    type: ConditionType
    lineno: int
    end_lineno: int | None = None
    condition_code: str | None = Field(None, description="Source code of the condition")


class FunctionAnalysis(BaseModel):
    """Analysis result for a single function."""

    name: str
    lineno: int
    end_lineno: int | None
    args: list[str] = Field(default_factory=list, description="Argument list")
    branches: list[BranchInfo] = Field(
        default_factory=list, description="Detected branches"
    )
    mock_candidates: list[MockCandidate] = Field(
        default_factory=list, description="Detected mock candidates"
    )
    cyclomatic_complexity: int = Field(0, description="Cyclomatic complexity")


class AnalyzeConditionResult(BaseModel):
    """Result of the condition analysis tool."""

    file_path: str
    functions: list[FunctionAnalysis] = Field(default_factory=list)
    error: str | None = None


def _is_builtin(name: str) -> bool:
    """Check if the name is a Python builtin."""
    return name in builtins.__dict__


# Standard library modules that should not be mocked
STDLIB_MODULES = {
    # Core
    "re",
    "json",
    "os",
    "sys",
    "pathlib",
    "datetime",
    "time",
    "collections",
    "itertools",
    "functools",
    "typing",
    # I/O
    "io",
    "tempfile",
    "shutil",
    "glob",
    # Data structures
    "dataclasses",
    "enum",
    "abc",
    # Encoding
    "base64",
    "hashlib",
    "hmac",
    "uuid",
    # Math
    "math",
    "random",
    "statistics",
    "decimal",
    # String
    "string",
    "textwrap",
    # Other common stdlib
    "copy",
    "pickle",
    "shelve",
    "warnings",
    "logging",
}


def _is_stdlib_call(func_name: str) -> bool:
    """
    Check if the function call is from standard library.

    Args:
        func_name: Function name (e.g., 're.search', 'json.dumps', 'Path.exists')

    Returns:
        True if it's a standard library call that should not be mocked
    """
    # Check for direct stdlib class/function names (without dots)
    # Common stdlib classes that are often imported directly
    stdlib_classes = {
        "Path",
        "datetime",
        "timedelta",
        "Decimal",
        "Counter",
        "defaultdict",
    }
    if func_name in stdlib_classes:
        return True

    if "." not in func_name:
        return False

    parts = func_name.split(".")
    base_module = parts[0]

    # Check if base module is in stdlib
    if base_module in STDLIB_MODULES:
        return True

    # Special case: pathlib.Path -> Path.method
    if base_module in stdlib_classes:
        return True

    return False


def _ast_unparse_safe(node: ast.AST) -> str | None:
    """Safely unparse an AST node to string."""
    try:
        return ast.unparse(node)
    except Exception:
        return None


class FunctionVisitor(ast.NodeVisitor):
    """Visitor to analyze a specific function node."""

    def __init__(self):
        self.branches: list[BranchInfo] = []
        self.mock_candidates: list[MockCandidate] = []
        self.complexity = 1  # Base complexity
        self._in_orelse = False  # Track if in orelse block (for ELIF detection)

    def visit_If(self, node: ast.If):
        # Determine if it's an 'elif' based on whether we're in an orelse block
        branch_type = ConditionType.ELIF if self._in_orelse else ConditionType.IF

        condition_code = _ast_unparse_safe(node.test)
        self.branches.append(
            BranchInfo(
                type=branch_type,
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                condition_code=condition_code,
            )
        )
        self.complexity += 1

        # Process body
        for child in node.body:
            self.visit(child)

        # Process else/elif
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                # This is an ELIF - mark it for the recursive call
                self._in_orelse = True
                self.visit(node.orelse[0])
                self._in_orelse = False
            else:
                # This is an ELSE
                self.branches.append(
                    BranchInfo(
                        type=ConditionType.ELSE,
                        lineno=node.orelse[0].lineno,
                        end_lineno=node.orelse[-1].end_lineno,
                        condition_code=None,
                    )
                )
                for child in node.orelse:
                    self.visit(child)

    def visit_For(self, node: ast.For):
        condition_code = f"in {_ast_unparse_safe(node.iter)}"
        self.branches.append(
            BranchInfo(
                type=ConditionType.FOR,
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                condition_code=condition_code,
            )
        )
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        condition_code = f"in {_ast_unparse_safe(node.iter)}"
        self.branches.append(
            BranchInfo(
                type=ConditionType.FOR,
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                condition_code=condition_code,
            )
        )
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        condition_code = _ast_unparse_safe(node.test)
        self.branches.append(
            BranchInfo(
                type=ConditionType.WHILE,
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                condition_code=condition_code,
            )
        )
        self.complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        self.branches.append(
            BranchInfo(
                type=ConditionType.TRY,
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                condition_code=None,
            )
        )
        for handler in node.handlers:
            condition_code = (
                _ast_unparse_safe(handler.type) if handler.type else "Exception"
            )
            self.branches.append(
                BranchInfo(
                    type=ConditionType.EXCEPT,
                    lineno=handler.lineno,
                    end_lineno=handler.end_lineno,
                    condition_code=condition_code,
                )
            )
            self.complexity += 1
            for child in handler.body:
                self.visit(child)

        for child in node.body:
            self.visit(child)
        for child in node.orelse:
            self.visit(child)
        for child in node.finalbody:
            self.visit(child)

    def visit_Match(self, node: ast.Match):
        self.branches.append(
            BranchInfo(
                type=ConditionType.MATCH,
                lineno=node.lineno,
                end_lineno=node.end_lineno,
                condition_code=_ast_unparse_safe(node.subject),
            )
        )
        for case in node.cases:
            self.branches.append(
                BranchInfo(
                    type=ConditionType.CASE,
                    lineno=case.pattern.lineno,
                    end_lineno=case.pattern.end_lineno,
                    condition_code=_ast_unparse_safe(case.pattern),
                )
            )
            self.complexity += 1
            for child in case.body:
                self.visit(child)

    def visit_Call(self, node: ast.Call):
        func_name = ""
        is_attribute_call = False

        if isinstance(node.func, ast.Attribute):
            # e.g., self.repo.save, client.get
            value_name = _ast_unparse_safe(node.func.value)
            if value_name:
                func_name = f"{value_name}.{node.func.attr}"
                is_attribute_call = value_name == "self" or value_name.startswith(
                    "self."
                )
        elif isinstance(node.func, ast.Name):
            # e.g., my_func()
            func_name = node.func.id
            is_attribute_call = False

        if func_name:
            # For attribute calls, check only the final attribute name for builtins
            check_name = func_name.split(".")[-1] if "." in func_name else func_name

            # Filter out builtins and standard library calls
            if not _is_builtin(check_name) and not _is_stdlib_call(func_name):
                self.mock_candidates.append(
                    MockCandidate(
                        name=func_name,
                        lineno=node.lineno,
                        end_lineno=node.end_lineno,
                        is_attribute_call=is_attribute_call,
                    )
                )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Do not recurse into nested functions for this visitor
        # We handle them separately at top-level or ignore to avoid confusion
        pass

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        pass


def _process_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> FunctionAnalysis:
    """Process a single function node and return its analysis."""
    visitor = FunctionVisitor()
    for child in node.body:
        visitor.visit(child)

    # Extract args including keyword-only args
    args = [arg.arg for arg in node.args.args]
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwonlyargs:
        for arg in node.args.kwonlyargs:
            args.append(arg.arg)
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")

    return FunctionAnalysis(
        name=node.name,
        lineno=node.lineno,
        end_lineno=node.end_lineno,
        args=args,
        branches=visitor.branches,
        mock_candidates=visitor.mock_candidates,
        cyclomatic_complexity=visitor.complexity,
    )


def py_condition_analyzer(
    file_path: str, function_name: str | None = None
) -> ToolResult[AnalyzeConditionResult]:
    """
    Analyzes a Python file to extract control flow conditions and mock candidates.

    Args:
        file_path: Path to the Python file.
        function_name: Optional function name to filter analysis.

    Returns:
        ToolResult containing detailed analysis of conditions and mock candidates.
    """
    try:
        repo = FileRepositoryFactory.create()

        if not repo.exists(file_path):
            return ToolResult(error=f"File not found: {file_path}")

        if not file_path.endswith(".py"):
            return ToolResult(error=f"Not a Python file: {file_path}")

        source_code = repo.read_text(file_path)
        tree = ast.parse(source_code)

        result = AnalyzeConditionResult(file_path=file_path)

        # Process only top-level functions and class methods
        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if function_name and node.name != function_name:
                    continue
                result.functions.append(_process_function(node))
            elif isinstance(node, ast.ClassDef):
                # Process methods in classes
                for class_node in node.body:
                    if isinstance(class_node, ast.FunctionDef | ast.AsyncFunctionDef):
                        if function_name and class_node.name != function_name:
                            continue
                        result.functions.append(_process_function(class_node))

        if function_name and not result.functions:
            return ToolResult(
                error=f"Function '{function_name}' not found in {file_path}"
            )

        return ToolResult(data=result)

    except SyntaxError as e:
        return ToolResult(error=f"Syntax error in file: {e}")
    except Exception as e:
        return ToolResult(error=f"Analysis failed: {e}")
