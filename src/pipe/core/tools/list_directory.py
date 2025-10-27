import fnmatch
import os
from typing import Any


def list_directory(
    path: str,
    file_filtering_options: dict[str, Any] | None = None,
    ignore: list[str] | None = None,
) -> dict[str, Any]:
    """
    Lists the names of files and subdirectories directly within a specified directory.
    """
    try:
        target_path = os.path.abspath(path)

        if not os.path.exists(target_path):
            return {"error": f"Path does not exist: {path}"}
        if not os.path.isdir(target_path):
            return {"error": f"Path is not a directory: {path}"}

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

        return {"files": sorted(files), "directories": sorted(directories)}
    except Exception as e:
        return {"error": f"Failed to list directory {path}: {str(e)}"}
