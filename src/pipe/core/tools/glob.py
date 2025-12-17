import os

from pipe.core.models.results.glob_result import GlobResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.repositories.filesystem_repository import FileSystemRepository
from pipe.core.utils.path import get_project_root


def glob(
    pattern: str, path: str | None = None, recursive: bool | None = True
) -> ToolResult[GlobResult]:
    """
    Efficiently finds files matching specific glob patterns, respecting .gitignore.
    """
    try:
        project_root = get_project_root()
        repo = FileSystemRepository(project_root)

        search_path = path if path else project_root

        # repo.glob returns absolute paths
        files = repo.glob(
            pattern,
            search_path=search_path,
            recursive=recursive if recursive is not None else True,
            respect_gitignore=True,
        )

        # Convert to relative paths to match original behavior
        rel_files = [os.path.relpath(f, project_root) for f in files]

        # Sort by name descending as a default (matching original tool)
        rel_files.sort(reverse=True)

        content_string = "\n".join(rel_files)
        result = GlobResult(content=content_string)
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(error=f"Error inside glob tool: {str(e)}")
