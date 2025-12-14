"""Sessions list backup action."""

from pipe.web.action_responses import BackupListResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.service_container import get_session_management_service


class SessionsListBackupAction(BaseAction):
    """
    Action to list sessions in the backup directory.

    Returns a list of sessions found in the backup directory with their
    session IDs and file paths.
    """

    def execute(self) -> BackupListResponse:
        sessions = get_session_management_service().list_backup_sessions()
        return BackupListResponse(sessions=sessions)
