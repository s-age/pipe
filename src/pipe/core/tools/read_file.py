import os

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory
from pipe.core.models.results.read_file_result import ReadFileResult


# session_manager and session_id are dynamically passed by the tool executor
def read_file(
    absolute_path: str,
    limit: float | None = None,
    offset: float | None = None,
    session_service=None,
    session_id=None,
) -> ReadFileResult:
    """
    Reads and returns the content of a specified file.
    If a session_id is provided, it also adds the file to the session's reference list.
    """
    abs_path = os.path.abspath(absolute_path)

    if not os.path.exists(abs_path):
        return ReadFileResult(error=f"File not found: {abs_path}")
    if not os.path.isfile(abs_path):
        return ReadFileResult(error=f"Path is not a file: {abs_path}")

    session_message = ""
    # Resolve session_id from env if not provided
    if not session_id:
        session_id = os.environ.get("PIPE_SESSION_ID")

    if session_id:
        try:
            project_root = os.getcwd()
            settings = SettingsFactory.get_settings(project_root)
            factory = ServiceFactory(project_root, settings)
            reference_service = factory.create_session_reference_service()

            reference_service.add_reference_to_session(session_id, abs_path)
            reference_service.update_reference_ttl_in_session(session_id, abs_path, 3)

            if os.path.getsize(abs_path) == 0:
                session_message = (
                    f"File '{abs_path}' has been added or updated in session "
                    "references, but it is empty."
                )
            else:
                session_message = (
                    f"File '{abs_path}' has been added or updated in session "
                    "references."
                )
        except Exception as e:
            # Don't fail the entire read_file operation if session reference fails
            session_message = (
                f"Warning: Failed to add or update reference in session: {e}"
            )

    # Always read the file content
    try:
        with open(abs_path, encoding="utf-8") as f:
            lines = f.readlines()

        if offset is not None:
            start = int(offset)
        else:
            start = 0

        if limit is not None:
            end = start + int(limit)
            lines_slice = lines[start:end]
        else:
            lines_slice = lines[start:]

        content = "".join(lines_slice)

        return ReadFileResult(
            content=content, message=session_message if session_message else None
        )
    except UnicodeDecodeError:
        return ReadFileResult(
            error=(f"Cannot decode file {abs_path} as text. It might be a binary file.")
        )
    except Exception as e:
        # If session_message exists, combine it with the file read error
        if session_message:
            return ReadFileResult(
                error=f"{session_message} Also, failed to read file: {e}"
            )
        else:
            return ReadFileResult(error=f"Failed to read file: {e}")
