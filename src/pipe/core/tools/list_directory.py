from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.results.list_directory_result import ListDirectoryResult
from pipe.core.models.tool_result import ToolResult


def list_directory(
    path: str,
    ignore: list[str] | None = None,
) -> ToolResult[ListDirectoryResult]:
    """
    Lists the names of files and subdirectories directly within a specified directory.
    """
    try:
        repo = FileRepositoryFactory.create()

        files, directories = repo.list_directory(path, ignore=ignore)

        result = ListDirectoryResult(files=files, directories=directories)
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(error=f"Failed to list directory {path}: {str(e)}")
