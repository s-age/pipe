import difflib
import os

from pipe.core.models.results.write_file_result import WriteFileResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.repositories.filesystem_repository import FileSystemRepository
from pipe.core.utils.path import get_project_root


def write_file(
    file_path: str, content: str, project_root: str | None = None
) -> ToolResult[WriteFileResult]:
    """
    Writes content to a specified file.
    """
    try:
        if project_root:
            project_root = os.path.abspath(project_root)
        else:
            project_root = get_project_root()

        repo = FileSystemRepository(project_root)

        original_content = ""
        if repo.exists(file_path) and repo.is_file(file_path):
            original_content = repo.read_text(file_path)

        repo.write_text(file_path, content)

        diff = None
        if original_content:
            diff_lines = difflib.unified_diff(
                original_content.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm="",
            )
            diff = "\n".join(list(diff_lines))

        message = f"File written successfully: {file_path}"
        if diff:
            message += f"\n\nDiff:\n```diff\n{diff}\n```"

        result = WriteFileResult(status="success", message=message, diff=diff)
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(error=f"Failed to write file {file_path}: {str(e)}")
