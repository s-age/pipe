import ast
import os
from typing import TypedDict

from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root


class SymbolReference(TypedDict):
    """A reference to a symbol in code."""

    file_path: str
    lineno: int
    line_content: str


class SymbolReferencesResult(TypedDict, total=False):
    """Result from finding symbol references."""

    references: list[SymbolReference]
    symbol_name: str
    reference_count: int
    error: str


def py_get_symbol_references(
    file_path: str, symbol_name: str, search_directory: str | None = None
) -> ToolResult[SymbolReferencesResult]:
    """
    Searches for references to a specific symbol across Python files.

    Args:
        file_path: The path to the file containing the symbol definition.
        symbol_name: The name of the symbol to search for.
        search_directory: Directory to search for references.
            Defaults to src/pipe in the project root.
    """
    if not os.path.exists(file_path):
        return ToolResult(error=f"File not found: {file_path}")

    # Default search_directory to src/pipe
    if search_directory is None:
        project_root = get_project_root()
        search_directory = os.path.join(project_root, "src", "pipe")

    if not os.path.isdir(search_directory):
        return ToolResult(error=f"Search directory not found: {search_directory}")

    # Verify the symbol exists in the source file
    with open(file_path, encoding="utf-8") as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return ToolResult(error=f"Syntax error in {file_path}: {e}")

    symbol_found = False
    symbol_lineno_start = -1
    symbol_lineno_end = -1

    # Check if the symbol exists in the file and determine its definition range
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ClassDef | ast.FunctionDef)
            and node.name == symbol_name
        ) or (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == symbol_name
                for target in node.targets
            )
        ):
            symbol_found = True
            symbol_lineno_start = node.lineno
            symbol_lineno_end = (
                node.end_lineno
                if hasattr(node, "end_lineno") and node.end_lineno is not None
                else node.lineno
            )
            break

    if not symbol_found:
        return ToolResult(error=f"Symbol '{symbol_name}' not found in {file_path}")

    # Collect all Python files in search_directory
    py_files: list[str] = []

    def walk_directory(directory: str) -> None:
        for root, dirs, files in os.walk(directory):
            # Skip common non-source directories
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    "__pycache__",
                    ".git",
                    ".venv",
                    "venv",
                    "node_modules",
                    ".pytest_cache",
                ]
            ]
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))

    walk_directory(search_directory)

    # Search for references in all Python files
    references: list[SymbolReference] = []
    file_path_abs = os.path.abspath(file_path)

    for py_file in py_files:
        py_file_abs = os.path.abspath(py_file)

        try:
            with open(py_file_abs, encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            continue

        for i, line in enumerate(lines):
            current_lineno = i + 1

            # Skip symbol definition lines in the original file
            if (
                py_file_abs == file_path_abs
                and symbol_lineno_start <= current_lineno <= symbol_lineno_end
            ):
                continue

            # Search for the symbol name in the line
            if symbol_name in line:
                references.append(
                    {
                        "file_path": py_file_abs,
                        "lineno": current_lineno,
                        "line_content": line.strip(),
                    }
                )

    result = {
        "symbol_name": symbol_name,
        "references": references,
        "reference_count": len(references),
    }
    return ToolResult(data=result)
