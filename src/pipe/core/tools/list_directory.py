from pipe.core.models.results.list_directory_result import ListDirectoryResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.repositories.filesystem_repository import FileSystemRepository
from pipe.core.utils.path import get_project_root


def list_directory(
    path: str,
    ignore: list[str] | None = None,
) -> ToolResult[ListDirectoryResult]:
    """
    Lists the names of files and subdirectories directly within a specified directory.
    """
    try:
        project_root = get_project_root()
        repo = FileSystemRepository(project_root)

        files, directories = repo.list_directory(path, ignore=ignore)

        result = ListDirectoryResult(files=files, directories=directories)
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(error=f"Failed to list directory {path}: {str(e)}")
