import difflib
import os

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.results.write_file_result import WriteFileResult
from pipe.core.models.tool_result import ToolResult


def write_file(
    file_path: str, content: str, project_root: str | None = None
) -> ToolResult[WriteFileResult]:
    """
    Writes content to a file. Creates new file or overwrites existing file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        project_root: Optional project root directory

    Returns:
        ToolResult containing WriteFileResult with:
        - status: "success" or error message
        - message: Confirmation message with diff (if file existed)
        - diff: Unified diff showing changes (None for new files)

    Notes:
        - Use triple quotes ('''content''') for multi-line strings
        - Escape backslashes: use \\\\ for a single backslash
        - Validate string is properly closed before calling

    Examples:
        Example 1 - Multi-line text files:
        GOOD: Use \n for line breaks
        write_file(
            file_path="config.txt",
            content="line1\nline2\nline3"
        )
        BAD: Spaces instead of newlines create single line
        write_file(
            file_path="config.txt",
            content="line1 line2 line3"
        )

        Example 2 - Python code with proper formatting:
        GOOD: Include \n and proper indentation
        write_file(
            file_path="test.py",
            content="def test():\n    x = 1\n    return x"
        )
        BAD: Missing newlines creates invalid syntax
        write_file(
            file_path="test.py",
            content="def test(): x = 1 return x"
        )

        Example 3 - Backslash escaping:
        GOOD: Double backslashes for Windows paths
        write_file(
            file_path="path.txt",
            content="C:\\\\Users\\\\data"
        )
        BAD: Single backslashes become escape sequences
        write_file(
            file_path="path.txt",
            content="C:\\Users\\data"
        )
    """
    try:
        # Normalize project_root if provided
        if project_root:
            project_root = os.path.abspath(project_root)

        # Create repository (auto-loads project_root and settings)
        repo = FileRepositoryFactory.create(project_root)

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
