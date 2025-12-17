import difflib

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.results.replace_result import ReplaceResult
from pipe.core.models.tool_result import ToolResult


def replace(
    file_path: str, instruction: str, old_string: str, new_string: str
) -> ToolResult[ReplaceResult]:
    """
    Replaces text within a file.
    """
    try:
        # Create repository (auto-loads project_root and settings)
        repo = FileRepositoryFactory.create()

        if not repo.exists(file_path):
            return ToolResult(error=f"File not found: {file_path}")
        if not repo.is_file(file_path):
            return ToolResult(error=f"Path is not a file: {file_path}")

        # Read content
        original_content = repo.read_text(file_path)

        # Perform simple string replacement (first occurrence only)
        if old_string not in original_content:
            return ToolResult(
                error=f"Old string not found in file: {file_path}",
            )

        new_content = original_content.replace(old_string, new_string, 1)

        # Write back modified content
        repo.write_text(file_path, new_content)

        diff = None
        if original_content != new_content:
            diff_lines = difflib.unified_diff(
                original_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                lineterm="",
            )
            diff = "\n".join(list(diff_lines))

        message = f"Text replaced successfully in {file_path}"
        if diff:
            message += f"\n\nDiff:\n```diff\n{diff}\n```"

        result = ReplaceResult(status="success", message=message, diff=diff)
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(
            error=f"Failed to replace text in file {file_path}: {str(e)}",
        )
