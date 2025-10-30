import ast
import os
from typing import Any


def py_analyze_code(file_path: str) -> dict[str, Any]:
    """
    Analyzes the AST of the given Python file for symbol information.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    with open(file_path, encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    symbols: dict[str, list[dict[str, Any]]] = {
        "classes": [],
        "functions": [],
        "variables": [],
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "docstring": ast.get_docstring(node),
            }
            symbols["classes"].append(class_info)
        elif isinstance(node, ast.FunctionDef):
            func_info = {
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "docstring": ast.get_docstring(node),
            }
            symbols["functions"].append(func_info)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_info = {
                        "name": target.id,
                        "lineno": target.lineno,
                        "end_lineno": target.end_lineno,
                    }
                    symbols["variables"].append(var_info)

    return symbols
