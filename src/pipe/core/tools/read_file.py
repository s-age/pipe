import os


# session_manager and session_id are dynamically passed by the tool executor
def read_file(
    absolute_path: str,
    limit: float | None = None,
    offset: float | None = None,
    session_service=None,
    session_id=None,
) -> dict[str, str]:
    """
    Adds a file to the session's reference list for inclusion in the prompt.
    It does not read the file content directly.
    """
    if not session_service or not session_id:
        return {"error": "This tool requires an active session."}

    abs_path = os.path.abspath(absolute_path)

    if not os.path.exists(abs_path):
        return {"error": f"File not found: {abs_path}"}
    if not os.path.isfile(abs_path):
        return {"error": f"Path is not a file: {abs_path}"}

    try:
        # First, ensure the reference exists with a default TTL if it's new.
        session_service.add_reference_to_session(session_id, abs_path)
        # Then, explicitly update the TTL to 3 to reset it if it already existed.
        session_service.update_reference_ttl_in_session(session_id, abs_path, 3)

        # Check if the file is empty and tailor the message
        if os.path.getsize(abs_path) == 0:
            message = (
                f"File '{abs_path}' has been added or updated in session "
                "references, but it is empty."
            )
        else:
            message = (
                f"File '{abs_path}' has been added or updated in session references."
            )

        return {"message": message}
    except Exception as e:
        return {"error": f"Failed to add or update reference in session: {e}"}
