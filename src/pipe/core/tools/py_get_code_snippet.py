import ast

from pipe.core.models.tool_result import ToolResult
from pipe.core.repositories.filesystem_repository import FileSystemRepository
from pipe.core.utils.path import get_project_root
from pydantic import BaseModel


class CodeSnippetResult(BaseModel):
    """Result from extracting code snippet."""

    snippet: str | None = None
    error: str | None = None


def py_get_code_snippet(
    file_path: str, symbol_name: str
) -> ToolResult[CodeSnippetResult]:
    """
    指定されたファイルから特定のシンボルのコードスニペットを抽出する。
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
        content = repo.read_text(file_path)
        lines = content.splitlines(keepends=True)

        # 既存のAST解析ロジック（変更なし）
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
                            if (
                                hasattr(node, "end_lineno")
                                and node.end_lineno is not None
                            )
                            else node.lineno
                        )
                        break
                if start_lineno != -1:
                    break

        if start_lineno == -1:
            return ToolResult(error=f"Symbol '{symbol_name}' not found in {file_path}")

        snippet_lines = lines[start_lineno - 1 : end_lineno]
        return ToolResult(data=CodeSnippetResult(snippet="".join(snippet_lines)))

    except UnicodeDecodeError:
        msg = f"Cannot decode file {file_path} as text. " "It might be a binary file."
        return ToolResult(error=msg)
    except ValueError as e:
        return ToolResult(error=f"Invalid file path: {e}")
    except Exception as e:
        return ToolResult(error=f"Failed to extract code snippet: {e}")
