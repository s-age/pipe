import fnmatch
import os
import sys

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory
from pipe.core.models.results.read_many_files_result import (
    FileContent,
    ReadManyFilesResult,
)
from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root


# session_service, session_id, and reference_service are dynamically passed by
# the tool executor
def read_many_files(
    paths: list[str],
    exclude: list[str] | None = None,
    include: list[str] | None = None,
    recursive: bool = True,
    useDefaultExcludes: bool = True,
    max_files: int = 20,  # Maximum number of files to read
    session_service=None,  # Deprecated, kept for interface compatibility
    session_id=None,
    reference_service=None,
) -> ToolResult[ReadManyFilesResult]:
    """
    Resolves file paths based on glob patterns and adds them to the session's
    reference list.

    Args:
        paths: List of file paths or glob patterns
        exclude: Patterns to exclude from results
        include: Patterns to include in results
        recursive: Whether to search recursively
        useDefaultExcludes: Whether to use default exclusion patterns
        max_files: Maximum number of files to read
        session_service: Session service instance (deprecated, kept for compatibility)
        session_id: Session ID for reference management (injected by tool executor)
        reference_service: Reference service instance (injected by tool executor)
    """
    if not session_id:
        session_id = os.environ.get("PIPE_SESSION_ID")

    project_root = get_project_root()

    repo = FileRepositoryFactory.create()

    # If reference_service is not provided (not injected), try to create it
    if session_id and not reference_service:
        try:
            settings = SettingsFactory.get_settings()
            factory = ServiceFactory(project_root, settings)
            reference_service = factory.create_session_reference_service()
        except Exception as e:
            print(f"Warning: Failed to setup reference service: {e}", file=sys.stderr)
            # If creation fails, we can't track references
            pass

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
            # Check if it is a directory using repo
            if repo.is_dir(pattern_or_path):
                pattern_to_glob = os.path.join(pattern_or_path, "**/*")
            else:
                pattern_to_glob = pattern_or_path

            # Use repo.glob without gitignore to allow manual filtering below
            for filepath in repo.glob(
                pattern_to_glob,
                search_path=project_root,
                recursive=recursive,
                respect_gitignore=False,
            ):
                # repo.glob returns absolute paths and verifies they exist and are files

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

                resolved_files.append(filepath)

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
                content = repo.read_text(fpath)
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
