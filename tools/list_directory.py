import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import fnmatch

def list_directory(path: str, file_filtering_options: Optional[Dict[str, Any]] = None, ignore: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Lists the names of files and subdirectories directly within a specified directory.
    """
    try:
        target_path = Path(path).resolve()

        if not target_path.exists():
            return {"error": f"Path does not exist: {path}"}
        if not target_path.is_dir():
            return {"error": f"Path is not a directory: {path}"}

        all_entries = os.listdir(target_path)
        files = []
        directories = []

        ignore_patterns = ignore if ignore is not None else []

        for entry in all_entries:
            # Apply ignore patterns
            if any(fnmatch.fnmatch(entry, pattern) for pattern in ignore_patterns):
                continue

            entry_path = target_path / entry
            if entry_path.is_file():
                files.append(entry)
            elif entry_path.is_dir():
                directories.append(entry)

        return {"files": sorted(files), "directories": sorted(directories)}
    except Exception as e:
        return {"error": f"Failed to list directory {path}: {str(e)}"}

