import fnmatch
import os
from typing import TypedDict

from pipe.core.models.results.list_directory_result import ListDirectoryResult
from pipe.core.models.tool_result import ToolResult


class FileFilteringOptions(TypedDict, total=False):
    """Options for filtering files in directory listing."""

    extensions: list[str]
    patterns: list[str]


def list_directory(
    path: str,
    file_filtering_options: FileFilteringOptions | None = None,
    ignore: list[str] | None = None,
) -> ToolResult[ListDirectoryResult]:
    """
    Lists the names of files and subdirectories directly within a specified directory.
    """
    try:
        target_path = os.path.abspath(path)

        if not os.path.exists(target_path):
            return ToolResult(error=f"Path does not exist: {path}")
        if not os.path.isdir(target_path):
            return ToolResult(error=f"Path is not a directory: {path}")

        all_entries = os.listdir(target_path)
        files = []
        directories = []

        ignore_patterns = ignore if ignore is not None else []

        for entry in all_entries:
            # Apply ignore patterns
            if any(fnmatch.fnmatch(entry, pattern) for pattern in ignore_patterns):
                continue

            entry_path = os.path.join(target_path, entry)
            if os.path.isfile(entry_path):
                files.append(entry)
            elif os.path.isdir(entry_path):
                directories.append(entry)

        result = ListDirectoryResult(
            files=sorted(files), directories=sorted(directories)
        )
        return ToolResult(data=result)
    except Exception as e:
        return ToolResult(error=f"Failed to list directory {path}: {str(e)}")
