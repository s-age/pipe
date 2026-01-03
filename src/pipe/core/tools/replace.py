import difflib

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.results.replace_result import ReplaceResult
from pipe.core.models.tool_result import ToolResult


def replace(
    file_path: str, instruction: str, old_string: str, new_string: str
) -> ToolResult[ReplaceResult]:
    """
    Replaces the first occurrence of text within a file.

    Args:
        file_path: Path to the file to modify
        instruction: Description of the replacement operation (for logging/tracking)
        old_string: Text to find (must match exactly including whitespace)
        new_string: Text to replace with

    Returns:
        ToolResult containing ReplaceResult with:
        - status: "success" or error message
        - message: Confirmation message with diff
        - diff: Unified diff showing the change

    Notes:
        - Only replaces the FIRST occurrence of old_string
        - old_string must match EXACTLY (character-for-character, including indentation)
        - Use triple quotes ('''content''') for multi-line strings
        - Escape backslashes: use \\\\ for a single backslash
        - Returns error if file not found or old_string not found

    Examples:
        Example 1 - Basic text replacement:
        GOOD: Complete match with exact content
        replace(
            file_path="config.py",
            instruction="Update version",
            old_string="VERSION = '1.0.0'",
            new_string="VERSION = '1.1.0'"
        )
        BAD: Partial match will fail if actual line has trailing comment
        replace(
            file_path="config.py",
            instruction="Update version",
            old_string="VERSION = ",
            new_string="VERSION = '2.0.0'"
        )

        Example 2 - Multi-line replacement:
        GOOD: Exact whitespace match including indentation
        replace(
            file_path="app.py",
            instruction="Update function",
            old_string="    def process():\n        return True",
            new_string="    def process():\n        return False"
        )
        BAD: Missing or wrong indentation will fail
        replace(
            file_path="app.py",
            instruction="Update function",
            old_string="def process():\n    return True",
            new_string="def process():\n    return False"
        )

        Example 3 - First occurrence only:
        GOOD: Specific enough to target first occurrence
        replace(
            file_path="utils.py",
            instruction="Fix first logger call",
            old_string="logger.info('starting process')",
            new_string="logger.debug('starting process')"
        )
        BAD: Too generic, only first match replaced, others remain
        replace(
            file_path="utils.py",
            instruction="Replace all info to debug",
            old_string="logger.info",
            new_string="logger.debug"
        )
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
