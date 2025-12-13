import fnmatch
import glob as std_glob
import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory


# session_service and session_id are dynamically passed by the tool executor
def read_many_files(
    paths: list[str],
    exclude: list[str] | None = None,
    include: list[str] | None = None,
    recursive: bool = True,
    useDefaultExcludes: bool = True,
    max_files: int = 5,  # New parameter for limiting file count
    session_service=None,  # Deprecated, kept for interface compatibility
    session_id=None,
) -> dict[str, str | list[dict[str, str]]]:
    """
    Resolves file paths based on glob patterns and adds them to the session's
    reference list.
    """
    if not session_id:
        session_id = os.environ.get("PIPE_SESSION_ID")

    project_root = os.getcwd()

    # If no session ID is provided, skip reference management
    if session_id:
        # Load settings
        try:
            settings = SettingsFactory.get_settings(project_root)
        except Exception as e:
            # If loading settings fails, log and proceed without reference service
            session_id = None  # Effectively disable reference management
            session_message = (
                f"Warning: Failed to load settings for reference management: {e}"
            )
        else:
            factory = ServiceFactory(project_root, settings)
            reference_service = factory.create_session_reference_service()
            session_message = ""
    else:
        session_message = "No active session. Files were not added to references."

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
            return {"files": [], "message": "No files found matching the criteria."}

        # Remove duplicates
        unique_files = sorted(list(set(resolved_files)))

        # Validate against max_files limit
        if len(unique_files) > max_files:
            return {
                "error": (
                    f"Too many files found ({len(unique_files)}). "
                    f"Maximum allowed is {max_files}. "
                    "Please refine your patterns or increase the 'max_files' limit."
                )
            }

        if session_id:
            if unique_files:  # Only add references if there are files
                reference_service.add_multiple_references(session_id, unique_files)
                if (
                    not session_message
                ):  # Overwrite if already set by non-active session
                    session_message = (
                        f"Added {len(unique_files)} files to the session references."
                    )
            elif not session_message:  # If no files and no prior session message
                session_message = "No files found to add to references."

        file_contents = []
        for fpath in unique_files:
            try:
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
                file_contents.append({"path": fpath, "content": content})
            except UnicodeDecodeError:
                file_contents.append(
                    {
                        "path": fpath,
                        "error": (
                            "Cannot decode file as text. It might be a binary file."
                        ),
                    }
                )
            except Exception as e:
                file_contents.append(
                    {"path": fpath, "error": f"Failed to read file: {e}"}
                )

        result: dict[str, str | list[dict[str, str]]] = {"files": file_contents}
        if session_message:
            result["message"] = session_message
        return result

    except Exception as e:
        # If session_message exists, combine it with the file read error
        if session_message:
            return {"error": f"{session_message} Also, failed to process files: {e}"}
        else:
            return {"error": f"Error in read_many_files tool: {str(e)}"}
