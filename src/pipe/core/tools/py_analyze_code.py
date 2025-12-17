import ast

from pipe.core.models.tool_result import ToolResult
from pipe.core.repositories.filesystem_repository import FileSystemRepository
from pipe.core.utils.path import get_project_root
from pydantic import BaseModel, Field


class SymbolInfo(BaseModel):
    """Information about a code symbol."""

    name: str
    lineno: int
    end_lineno: int | None = None
    docstring: str | None = None


class AnalyzeCodeResult(BaseModel):
    """Result from analyzing Python code."""

    classes: list[SymbolInfo] = Field(default_factory=list)
    functions: list[SymbolInfo] = Field(default_factory=list)
    variables: list[SymbolInfo] = Field(default_factory=list)
    error: str | None = None


def py_analyze_code(file_path: str) -> ToolResult[AnalyzeCodeResult]:
    """
    Analyzes the AST of the given Python file for symbol information.
    """
    try:
        project_root = get_project_root()
        repo = FileSystemRepository(project_root)

        # セキュリティチェック付きで存在確認
        if not repo.exists(file_path):
            return ToolResult(error=f"File not found: {file_path}")
        if not repo.is_file(file_path):
            return ToolResult(error=f"Path is not a file: {file_path}")

        # リポジトリ経由でファイル読み込み
        source_code = repo.read_text(file_path)

        tree = ast.parse(source_code)
        symbols = AnalyzeCodeResult()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = SymbolInfo(
                    name=node.name,
                    lineno=node.lineno,
                    end_lineno=node.end_lineno,
                    docstring=ast.get_docstring(node),
                )
                symbols.classes.append(class_info)
            elif isinstance(node, ast.FunctionDef):
                func_info = SymbolInfo(
                    name=node.name,
                    lineno=node.lineno,
                    end_lineno=node.end_lineno,
                    docstring=ast.get_docstring(node),
                )
                symbols.functions.append(func_info)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_info = SymbolInfo(
                            name=target.id,
                            lineno=target.lineno,
                            end_lineno=target.end_lineno,
                        )
                        symbols.variables.append(var_info)

        return ToolResult(data=symbols)

    except UnicodeDecodeError:
        msg = f"Cannot decode file {file_path} as text. " "It might be a binary file."
        return ToolResult(error=msg)
    except SyntaxError as e:
        return ToolResult(error=f"Syntax error in {file_path}: {e}")
    except ValueError as e:
        return ToolResult(error=f"Invalid file path: {e}")
    except Exception as e:
        return ToolResult(error=f"Failed to analyze code: {e}")
