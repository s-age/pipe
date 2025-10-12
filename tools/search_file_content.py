import re
import os
import glob as std_glob
from pathlib import Path
from typing import Optional

def search_file_content(
    pattern: str,
    include: Optional[str] = None,
    path: Optional[str] = None,
) -> dict:
    try:
        compiled_pattern = re.compile(pattern)
        project_root = Path(os.getcwd())

        search_path = project_root
        if path:
            abs_path = project_root / path
            if not abs_path.is_dir():
                return {"content": f"Error: Search path '{path}' is not a directory."}
            search_path = abs_path

        # Use glob to find files, filtered by include pattern if provided
        if include:
            glob_pattern = str(search_path / include)
        else:
            glob_pattern = str(search_path / "**/*")

        matches = []
        for filepath_str in std_glob.glob(glob_pattern, recursive=True):
            filepath = Path(filepath_str)
            if filepath.is_file():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if compiled_pattern.search(line):
                                matches.append({
                                    "file_path": str(filepath.relative_to(project_root)),
                                    "line_number": line_num,
                                    "line_content": line.strip()
                                })
                except UnicodeDecodeError:
                    # Skip binary files or files with encoding issues
                    continue
                except Exception as file_e:
                    matches.append({"error": f"Error reading file {filepath}: {str(file_e)}"})

        if not matches:
            return {"content": "No matches found."}

        return {"content": matches}

    except re.error as e:
        return {"content": f"Error: Invalid regex pattern: {str(e)}"}
    except Exception as e:
        return {"content": f"Error inside search_file_content tool: {str(e)}"}
