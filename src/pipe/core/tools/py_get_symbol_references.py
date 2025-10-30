import ast
import os
from typing import Any


def py_get_symbol_references(file_path: str, symbol_name: str) -> dict[str, Any]:
    """
    Searches for references to a specific symbol within the given Python file.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    with open(file_path, encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    references: list[dict[str, Any]] = []
    symbol_found = False

    # First, check if the symbol exists in the file and determine its definition range.
    symbol_lineno_start = -1
    symbol_lineno_end = -1

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
        return {"error": f"Symbol '{symbol_name}' not found in {file_path}"}

    # Search for references outside the symbol's definition range.
    lines = source_code.splitlines()
    for i, line in enumerate(lines):
        current_lineno = i + 1
        # Skip symbol definition lines.
        if symbol_lineno_start <= current_lineno <= symbol_lineno_end:
            continue

        # Search for lines where the symbol name is included as a string.
        if symbol_name in line:
            # AST-based reference counting is possible; using simple string search.
            # TODO: Implement more accurate AST-based reference counting.
            references.append({"lineno": current_lineno, "line_content": line.strip()})

    return {
        "symbol_name": symbol_name,
        "references": references,
        "reference_count": len(references),
    }
