import ast
import os
from typing import Any


def py_get_type_hints(file_path: str, symbol_name: str) -> dict[str, Any]:
    """
    指定されたPythonファイル内の関数またはクラスのタイプヒントを抽出する。
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    with open(file_path, encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    type_hints = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == symbol_name:
            for arg in node.args.args:
                if arg.annotation:
                    type_hints[arg.arg] = ast.unparse(arg.annotation)
            if node.returns:
                type_hints["return"] = ast.unparse(node.returns)
            break
        elif isinstance(node, ast.ClassDef) and node.name == symbol_name:
            # クラスレベルのタイプヒント（変数アノテーション）を抽出
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    if isinstance(item.target, ast.Name):
                        type_hints[item.target.id] = ast.unparse(item.annotation)
            break

    if not type_hints:
        return {
            "error": f"Type hints for symbol '{symbol_name}' not found in {file_path}"
        }

    return {"type_hints": type_hints}
