"""Unit tests for SessionsListBackupAction."""

from unittest.mock import MagicMock, patch

from pipe.core.collections.backup_files import SessionSummary
from pipe.web.action_responses import BackupListResponse
from pipe.web.actions.session_management.sessions_list_backup_action import (
    SessionsListBackupAction,
)


class TestSessionsListBackupAction:
    """Tests for SessionsListBackupAction."""

    @patch(
        "pipe.web.actions.session_management.sessions_list_backup_action.get_session_management_service"
    )
    def test_execute_success(self, mock_get_service):
        """Test execute returns BackupListResponse with sessions."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_sessions = [
            SessionSummary(
                session_id="session-1",
                file_path="/path/to/session-1.json",
                purpose="Test purpose 1",
                deleted_at="2025-01-01T00:00:00+09:00",
                session_data={"session_id": "session-1", "purpose": "Test purpose 1"},
            ),
            SessionSummary(
                session_id="session-2",
                file_path="/path/to/session-2.json",
                purpose="Test purpose 2",
                deleted_at="2025-01-01T01:00:00+09:00",
                session_data={"session_id": "session-2", "purpose": "Test purpose 2"},
            ),
        ]
        mock_service.list_backup_sessions.return_value = mock_sessions

        action = SessionsListBackupAction()

        # Execute
        response = action.execute()

        # Verify
        assert isinstance(response, BackupListResponse)
        assert response.sessions == mock_sessions
        mock_service.list_backup_sessions.assert_called_once()

    @patch(
        "pipe.web.actions.session_management.sessions_list_backup_action.get_session_management_service"
    )
    def test_execute_empty(self, mock_get_service):
        """Test execute returns empty list when no backups found."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.list_backup_sessions.return_value = []

        action = SessionsListBackupAction()

        # Execute
        response = action.execute()

        # Verify
        assert isinstance(response, BackupListResponse)
        assert response.sessions == []
        mock_service.list_backup_sessions.assert_called_once()
