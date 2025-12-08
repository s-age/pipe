"""Sessions list backup action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.service_container import get_session_management_service


class SessionsListBackupAction(BaseAction):
    """
    Action to list sessions in the backup directory.

    Returns a list of sessions found in the backup directory with their
    session IDs and file paths.
    """

    def execute(self) -> dict[str, list[dict]]:
        sessions = get_session_management_service().list_backup_sessions()
        # Convert SessionSummary objects to dicts for JSON serialization
        return {"sessions": [session.model_dump() for session in sessions]}
