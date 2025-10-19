import re
import os
import glob as std_glob

from typing import Optional

def search_file_content(
    pattern: str,
    include: Optional[str] = None,
    path: Optional[str] = None,
) -> dict:
    try:
        compiled_pattern = re.compile(pattern)
        project_root = os.getcwd()

        search_path = project_root
        if path:
            abs_path = os.path.join(project_root, path)
            if not os.path.isdir(abs_path):
                return {"content": f"Error: Search path '{path}' is not a directory."}
            search_path = abs_path

        # Use glob to find files, filtered by include pattern if provided
        if include:
            glob_pattern = os.path.join(search_path, include)
        else:
            glob_pattern = os.path.join(search_path, "**/*")

        matches = []
        for filepath_str in std_glob.glob(glob_pattern, recursive=True):
            filepath = filepath_str
            if os.path.isfile(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if compiled_pattern.search(line):
                                matches.append({
                                    "file_path": os.path.relpath(filepath, project_root),
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
