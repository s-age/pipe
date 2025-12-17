import os

from pipe.core.factories.file_repository_factory import FileRepositoryFactory
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.factories.settings_factory import SettingsFactory
from pipe.core.models.results.read_file_result import ReadFileResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.utils.path import get_project_root


# session_service, session_id, and reference_service are dynamically passed by
# the tool executor
def read_file(
    absolute_path: str,
    limit: int | None = None,
    offset: int | None = None,
    session_service=None,
    session_id=None,
    reference_service=None,
) -> ToolResult[ReadFileResult]:
    """
    Reads and returns the content of a specified file.
    If a session_id is provided, it also adds the file to the session's reference list.

    Args:
        absolute_path: Path to the file to read
        limit: Maximum number of lines to read (optional)
        offset: Number of lines to skip from the start (optional)
        session_service: Session service instance (injected by tool executor)
        session_id: Session ID for reference management (injected by tool executor)
        reference_service: Reference service instance (injected by tool executor)
    """
    # Create repository (auto-loads project_root and settings)
    repo = FileRepositoryFactory.create()
    project_root = get_project_root()

    if not repo.exists(absolute_path):
        return ToolResult(error=f"File not found: {absolute_path}")
    if not repo.is_file(absolute_path):
        return ToolResult(error=f"Path is not a file: {absolute_path}")

    # Use repository to get validated absolute path
    abs_path = repo.get_absolute_path(absolute_path)

    session_message = ""
    # Resolve session_id from env if not provided
    if not session_id:
        session_id = os.environ.get("PIPE_SESSION_ID")

    if session_id:
        try:
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
        content = repo.read_text(
            absolute_path, limit=limit, offset=offset if offset is not None else 0
        )

        result = ReadFileResult(
            content=content, message=session_message if session_message else None
        )
        return ToolResult(data=result)
    except UnicodeDecodeError:
        return ToolResult(
            error=(f"Cannot decode file {abs_path} as text. It might be a binary file.")
        )
    except Exception as e:
        # If session_message exists, combine it with the file read error
        if session_message:
            return ToolResult(error=f"{session_message} Also, failed to read file: {e}")
        else:
            return ToolResult(error=f"Failed to read file: {e}")
