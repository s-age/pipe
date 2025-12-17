import fnmatch
import glob as std_glob
import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory
from pipe.core.models.results.read_many_files_result import (
    FileContent,
    ReadManyFilesResult,
)
from pipe.core.models.tool_result import ToolResult


# session_service and session_id are dynamically passed by the tool executor
def read_many_files(
    paths: list[str],
    exclude: list[str] | None = None,
    include: list[str] | None = None,
    recursive: bool = True,
    useDefaultExcludes: bool = True,
    max_files: int = 20,  # Maximum number of files to read
    session_service=None,  # Deprecated, kept for interface compatibility
    session_id=None,
) -> ToolResult[ReadManyFilesResult]:
    """
    Resolves file paths based on glob patterns and adds them to the session's
    reference list.
    """
    if not session_id:
        session_id = os.environ.get("PIPE_SESSION_ID")

    project_root = os.getcwd()

    # If no session ID is provided, skip reference management
    reference_service = None
    if session_id:
        # Try to load settings and create reference service
        try:
            settings = SettingsFactory.get_settings(project_root)
            factory = ServiceFactory(project_root, settings)
            reference_service = factory.create_session_reference_service()
        except Exception:
            # If any setup fails, proceed without reference management (silently)
            session_id = None
            reference_service = None

    try:
        resolved_files = []
        # project_root is already defined above

        default_excludes = [
            "**/.git/**",
            "**/.gemini/**",
            "**/.pytest_cache/**",
            "**/__pycache__/**",
            "**/venv/**",
            "**/node_modules/**",
            "*.log",
            "*.tmp",
            "*.bak",
        ]

        final_excludes = set(exclude if exclude is not None else [])
        if useDefaultExcludes:
            final_excludes.update(default_excludes)

        final_includes = set(include if include is not None else [])

        for pattern_or_path in paths:
            # Handle directory paths
            if os.path.isdir(os.path.join(project_root, pattern_or_path)):
                pattern_to_glob = os.path.join(project_root, pattern_or_path, "**/*")
            else:
                pattern_to_glob = os.path.join(project_root, pattern_or_path)

            for filepath_str in std_glob.glob(pattern_to_glob, recursive=recursive):
                filepath = filepath_str

                if not os.path.isfile(filepath):
                    continue

                is_excluded = False
                basename = os.path.basename(filepath)
                relative_filepath = os.path.relpath(filepath, project_root)

                for p in final_excludes:
                    if (
                        fnmatch.fnmatch(filepath, p)
                        or fnmatch.fnmatch(relative_filepath, p)
                        or fnmatch.fnmatch(basename, p)
                    ):
                        is_excluded = True
                        break
                if is_excluded:
                    continue

                if final_includes:
                    is_included = any(
                        fnmatch.fnmatch(filepath, p) for p in final_includes
                    )
                    if not is_included:
                        continue

                resolved_files.append(os.path.abspath(filepath))

        if not resolved_files:
            result = ReadManyFilesResult(
                files=[], message="No files found matching the criteria."
            )
            return ToolResult(data=result)

        # Remove duplicates
        unique_files = sorted(list(set(resolved_files)))

        # Handle max_files limit: truncate if exceeded
        truncated = False
        total_found = len(unique_files)
        if len(unique_files) > max_files:
            truncated = True
            unique_files = unique_files[:max_files]

        if session_id and reference_service:
            if unique_files:  # Only add references if there are files
                try:
                    reference_service.add_multiple_references(session_id, unique_files)
                except Exception:
                    # If adding references fails, continue silently
                    pass

        file_contents = []
        for fpath in unique_files:
            try:
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
                file_contents.append(FileContent(path=fpath, content=content))
            except UnicodeDecodeError:
                file_contents.append(
                    FileContent(
                        path=fpath,
                        error=(
                            "Cannot decode file as text. It might be a binary file."
                        ),
                    )
                )
            except Exception as e:
                file_contents.append(
                    FileContent(path=fpath, error=f"Failed to read file: {e}")
                )

        # Add truncation warning if applicable
        message = None
        if truncated:
            message = (
                f"Found {total_found} files but showing only the first {max_files}. "
                f"Use a more specific pattern or increase 'max_files' to see more."
            )

        result = ReadManyFilesResult(
            files=file_contents,
            message=message,
        )
        return ToolResult(data=result)

    except Exception as e:
        return ToolResult(error=f"Error in read_many_files tool: {str(e)}")
