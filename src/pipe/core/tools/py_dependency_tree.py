import ast
from pathlib import Path

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.tool_result import ToolResult
from pydantic import BaseModel, Field


class DependencyNode(BaseModel):
    """A node in the dependency tree."""

    name: str
    source: str
    dependencies: "DependencyTreeResult | None" = None


class DependencyTreeResult(BaseModel):
    """Result from building a dependency tree."""

    file_path: str
    classes: list[DependencyNode] = Field(default_factory=list)
    functions: list[DependencyNode] = Field(default_factory=list)
    imports: list[DependencyNode] = Field(default_factory=list)
    decorators: list[DependencyNode] = Field(default_factory=list)
    circular: bool = False
    max_depth_reached: bool = False


def py_dependency_tree(
    file_path: str, max_depth: int = 3
) -> ToolResult[DependencyTreeResult]:
    """
    Builds a dependency tree for a Python file.

    Args:
        file_path: Path to a Python file
        max_depth: Maximum depth to traverse (default: 3)

    Returns:
        ToolResult containing a tree of dependencies including:
        - Classes instantiated or inherited
        - Functions called
        - Modules imported
        - Decorators used
    """
    try:
        repo = FileRepositoryFactory.create()

        if not repo.exists(file_path):
            return ToolResult(error=f"File not found: {file_path}")

        if not file_path.endswith(".py"):
            return ToolResult(error=f"Not a Python file: {file_path}")

        # Build the dependency tree
        visited: set[str] = set()
        result = _build_dependency_tree(file_path, max_depth, visited, repo)

        return ToolResult(data=result)

    except ValueError as e:
        return ToolResult(error=f"Invalid path: {e}")
    except Exception as e:
        return ToolResult(error=f"An unexpected error occurred: {e}")


def _build_dependency_tree(
    file_path: str,
    max_depth: int,
    visited: set[str],
    repo,
    current_depth: int = 0,
) -> DependencyTreeResult:
    """Recursively build dependency tree for a Python file."""
    abs_path = str(Path(file_path).resolve())

    # Check for circular dependencies
    if abs_path in visited:
        return DependencyTreeResult(file_path=file_path, circular=True)

    # Check max depth
    if current_depth >= max_depth:
        return DependencyTreeResult(file_path=file_path, max_depth_reached=True)

    visited.add(abs_path)
    result = DependencyTreeResult(file_path=file_path)

    try:
        source_code = repo.read_text(file_path)
        tree = ast.parse(source_code)

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dep_node = DependencyNode(
                        name=alias.name, source="import", dependencies=None
                    )
                    result.imports.append(dep_node)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Try to resolve relative imports
                    module_path = _resolve_import_path(
                        file_path, node.module, node.level
                    )
                    if module_path and repo.exists(module_path):
                        # Recursively analyze this module
                        child_tree = _build_dependency_tree(
                            module_path,
                            max_depth,
                            visited.copy(),
                            repo,
                            current_depth + 1,
                        )
                        for alias in node.names:
                            dep_node = DependencyNode(
                                name=alias.name,
                                source=node.module,
                                dependencies=(
                                    child_tree if not child_tree.circular else None
                                ),
                            )
                            result.imports.append(dep_node)
                    else:
                        # External module or unresolvable
                        for alias in node.names:
                            dep_node = DependencyNode(
                                name=alias.name,
                                source=node.module or "",
                                dependencies=None,
                            )
                            result.imports.append(dep_node)

        # Extract function calls and class instantiations at module level
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                # Analyze function body for calls
                func_calls = _extract_function_calls(node)
                for call_name in func_calls:
                    dep_node = DependencyNode(
                        name=call_name,
                        source="function_call",
                        dependencies=None,
                    )
                    result.functions.append(dep_node)

                # Extract decorators
                for decorator in node.decorator_list:
                    decorator_name = _get_decorator_name(decorator)
                    if decorator_name:
                        dep_node = DependencyNode(
                            name=decorator_name, source="decorator", dependencies=None
                        )
                        result.decorators.append(dep_node)

            elif isinstance(node, ast.ClassDef):
                # Extract base classes
                for base in node.bases:
                    base_name = _get_name_from_node(base)
                    if base_name:
                        dep_node = DependencyNode(
                            name=base_name, source="base_class", dependencies=None
                        )
                        result.classes.append(dep_node)

                # Extract class decorators
                for decorator in node.decorator_list:
                    decorator_name = _get_decorator_name(decorator)
                    if decorator_name:
                        dep_node = DependencyNode(
                            name=decorator_name, source="decorator", dependencies=None
                        )
                        result.decorators.append(dep_node)

                # Analyze methods for calls
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        func_calls = _extract_function_calls(item)
                        for call_name in func_calls:
                            dep_node = DependencyNode(
                                name=call_name,
                                source="function_call",
                                dependencies=None,
                            )
                            result.functions.append(dep_node)

    except SyntaxError:
        pass
    except Exception:
        pass

    visited.discard(abs_path)
    return result


def _resolve_import_path(current_file: str, module_name: str, level: int) -> str | None:
    """Resolve a Python import to an actual file path."""
    current_path = Path(current_file).resolve().parent

    # Handle relative imports (level > 0)
    if level > 0:
        # Go up 'level' directories
        for _ in range(level):
            current_path = current_path.parent

    # Convert module name to path
    module_parts = module_name.split(".")
    module_path = current_path / "/".join(module_parts)

    # Try both __init__.py and direct .py file
    if (module_path / "__init__.py").exists():
        return str(module_path / "__init__.py")
    elif module_path.with_suffix(".py").exists():
        return str(module_path.with_suffix(".py"))

    return None


def _extract_function_calls(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Extract function calls from a function/method body."""
    calls: set[str] = set()

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func_name = _get_name_from_node(child.func)
            if func_name:
                calls.add(func_name)

    return calls


def _get_name_from_node(node: ast.AST) -> str | None:
    """Extract name from an AST node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        # For attribute access like obj.method, return full path
        value = _get_name_from_node(node.value)
        if value:
            return f"{value}.{node.attr}"
        return node.attr
    return None


def _get_decorator_name(node: ast.AST) -> str | None:
    """Extract decorator name from a decorator node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Call):
        return _get_name_from_node(node.func)
    elif isinstance(node, ast.Attribute):
        return _get_name_from_node(node)
    return None


def format_dependency_tree(tree: DependencyTreeResult, indent: str = "") -> str:
    """Format the dependency tree as a readable string."""
    lines = [f"{tree.file_path}"]

    if tree.circular:
        lines.append(f"{indent}  [CIRCULAR DEPENDENCY DETECTED]")
        return "\n".join(lines)

    if tree.max_depth_reached:
        lines.append(f"{indent}  [Max depth reached]")

    if tree.imports:
        lines.append(f"{indent}├─ Imports")
        for i, imp in enumerate(tree.imports):
            is_last = i == len(tree.imports) - 1 and not (
                tree.classes or tree.functions or tree.decorators
            )
            prefix = "└─" if is_last else "├─"
            lines.append(f"{indent}│  {prefix} {imp.name} ({imp.source})")
            if imp.dependencies and not imp.dependencies.circular:
                child_indent = indent + ("   " if is_last else "│  ")
                child_tree = format_dependency_tree(imp.dependencies, child_indent)
                child_lines = child_tree.split("\n")[1:]
                lines.extend(child_lines)

    if tree.classes:
        lines.append(f"{indent}├─ Classes")
        for i, cls in enumerate(tree.classes):
            is_last = i == len(tree.classes) - 1 and not (
                tree.functions or tree.decorators
            )
            prefix = "└─" if is_last else "├─"
            lines.append(f"{indent}│  {prefix} {cls.name} ({cls.source})")
            if cls.dependencies and not cls.dependencies.circular:
                child_indent = indent + ("   " if is_last else "│  ")
                child_tree = format_dependency_tree(cls.dependencies, child_indent)
                child_lines = child_tree.split("\n")[1:]
                lines.extend(child_lines)

    if tree.functions:
        lines.append(f"{indent}├─ Functions")
        for i, func in enumerate(tree.functions):
            is_last = i == len(tree.functions) - 1 and not tree.decorators
            prefix = "└─" if is_last else "├─"
            lines.append(f"{indent}│  {prefix} {func.name} ({func.source})")
            if func.dependencies and not func.dependencies.circular:
                child_indent = indent + ("   " if is_last else "│  ")
                child_tree = format_dependency_tree(func.dependencies, child_indent)
                child_lines = child_tree.split("\n")[1:]
                lines.extend(child_lines)

    if tree.decorators:
        lines.append(f"{indent}└─ Decorators")
        for i, dec in enumerate(tree.decorators):
            is_last = i == len(tree.decorators) - 1
            prefix = "└─" if is_last else "├─"
            lines.append(f"{indent}   {prefix} {dec.name} ({dec.source})")
            if dec.dependencies and not dec.dependencies.circular:
                child_indent = indent + ("   " if is_last else "   ")
                child_tree = format_dependency_tree(dec.dependencies, child_indent)
                child_lines = child_tree.split("\n")[1:]
                lines.extend(child_lines)

    return "\n".join(lines)
