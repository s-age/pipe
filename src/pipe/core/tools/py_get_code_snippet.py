import ast
import os
from typing import TypedDict


class CodeSnippetResult(TypedDict, total=False):
    """Result from extracting code snippet."""

    snippet: str
    error: str


def py_get_code_snippet(file_path: str, symbol_name: str) -> CodeSnippetResult:
    """
    指定されたファイルから特定のシンボルのコードスニペットを抽出する。
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    tree = ast.parse("".join(lines))
    start_lineno = -1
    end_lineno = -1

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ClassDef | ast.FunctionDef)
            and node.name == symbol_name
        ):
            start_lineno = node.lineno
            end_lineno = (
                node.end_lineno
                if hasattr(node, "end_lineno") and node.end_lineno is not None
                else node.lineno
            )
            break
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == symbol_name:
                    start_lineno = node.lineno
                    end_lineno = (
                        node.end_lineno
                        if hasattr(node, "end_lineno") and node.end_lineno is not None
                        else node.lineno
                    )
                    break
            if start_lineno != -1:
                break

    if start_lineno == -1:
        return {"error": f"Symbol '{symbol_name}' not found in {file_path}"}

    snippet_lines = lines[start_lineno - 1 : end_lineno]
    return {"snippet": "".join(snippet_lines)}
