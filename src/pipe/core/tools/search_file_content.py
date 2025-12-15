import glob as std_glob
import os
import re

from pipe.core.models.results.search_file_content_result import (
    FileMatchItem,
    SearchFileContentResult,
)


def search_file_content(
    pattern: str,
    include: str | None = None,
    path: str | None = None,
) -> SearchFileContentResult:
    try:
        compiled_pattern = re.compile(pattern)
        project_root = os.getcwd()

        search_path = path if path else project_root
        if not os.path.isabs(search_path):
            search_path = os.path.abspath(os.path.join(project_root, search_path))

        if not os.path.isdir(search_path):
            return SearchFileContentResult(
                content=f"Error: Search path '{path}' is not a directory."
            )

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
                    with open(filepath, encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if compiled_pattern.search(line):
                                matches.append(
                                    FileMatchItem(
                                        file_path=os.path.relpath(
                                            filepath, search_path
                                        ),
                                        line_number=line_num,
                                        line_content=line.strip(),
                                    )
                                )
                except UnicodeDecodeError:
                    # Skip binary files or files with encoding issues
                    continue
                except Exception as file_e:
                    matches.append(
                        FileMatchItem(
                            error=f"Error reading file {filepath}: {str(file_e)}"
                        )
                    )

        if not matches:
            return SearchFileContentResult(content="No matches found.")

        return SearchFileContentResult(content=matches)

    except re.error as e:
        return SearchFileContentResult(
            content=f"Error: Invalid regex pattern: {str(e)}"
        )
    except Exception as e:
        return SearchFileContentResult(
            content=f"Error inside search_file_content tool: {str(e)}"
        )
