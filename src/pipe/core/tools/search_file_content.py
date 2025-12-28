import os
import re

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.models.results.search_file_content_result import (
    FileMatchItem,
    SearchFileContentResult,
)
from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root


def search_file_content(
    pattern: str,
    include: str | None = None,
    path: str | None = None,
) -> ToolResult[SearchFileContentResult]:
    try:
        compiled_pattern = re.compile(pattern)
        project_root = get_project_root()
        repo = FileRepositoryFactory.create()

        search_path = path if path else project_root

        # repo verifies existence and directory
        if not repo.exists(search_path):
            return ToolResult(error=f"Error: Search path '{path}' not found.")
        if not repo.is_dir(search_path):
            return ToolResult(error=f"Error: Search path '{path}' is not a directory.")

        # Use repo.glob
        glob_pattern = include if include else "**/*"

        # repo.glob returns absolute paths
        # Output relative paths (to search_path) to match original behavior

        matches = []
        # Use recursive=True default matching original logic.
        # We respect gitignore here to avoid searching in ignored files like
        # node_modules, .git, build artifacts, etc.
        files = repo.glob(
            glob_pattern,
            search_path=search_path,
            recursive=True,
            respect_gitignore=True,
        )

        for filepath in files:
            if not repo.is_file(filepath):
                continue

            try:
                # read_text reads whole file. fine for now.
                content = repo.read_text(filepath)

                for line_num, line in enumerate(content.splitlines(), 1):
                    if compiled_pattern.search(line):
                        matches.append(
                            FileMatchItem(
                                file_path=os.path.relpath(
                                    filepath,
                                    (
                                        search_path
                                        if os.path.isabs(search_path)
                                        else os.path.abspath(search_path)
                                    ),
                                ),
                                line_number=line_num,
                                line_content=line.strip(),
                            )
                        )
            except UnicodeDecodeError:
                # Skip binary files
                continue
            except Exception as file_e:
                matches.append(
                    FileMatchItem(error=f"Error reading file {filepath}: {str(file_e)}")
                )

        if not matches:
            result = SearchFileContentResult(content="No matches found.")
            return ToolResult(data=result)

        result = SearchFileContentResult(content=matches)
        return ToolResult(data=result)

    except re.error as e:
        return ToolResult(error=f"Error: Invalid regex pattern: {str(e)}")
    except Exception as e:
        return ToolResult(error=f"Error inside search_file_content tool: {str(e)}")
