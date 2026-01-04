"""Unit tests for SessionsDeleteBackupAction."""

from unittest.mock import MagicMock

import pytest
from pipe.core.services.session_management_service import SessionManagementService
from pipe.web.actions.session_management.sessions_delete_backup_action import (
    SessionsDeleteBackupAction,
)
from pipe.web.requests.sessions.delete_sessions import DeleteBackupRequest


class TestSessionsDeleteBackupAction:
    """Tests for SessionsDeleteBackupAction."""

    @pytest.fixture
    def mock_service(self) -> MagicMock:
        """Create a mock SessionManagementService."""
        return MagicMock(spec=SessionManagementService)

    def test_init(self, mock_service: MagicMock):
        """Test initialization of SessionsDeleteBackupAction."""
        request = DeleteBackupRequest(session_ids=["session-1"])
        action = SessionsDeleteBackupAction(
            session_management_service=mock_service, validated_request=request
        )

        assert action.session_management_service == mock_service
        assert action.validated_request == request

    def test_execute_with_session_ids(self, mock_service: MagicMock):
        """Test execute method with session_ids."""
        session_ids = ["session-1", "session-2"]
        request = DeleteBackupRequest(session_ids=session_ids)
        mock_service.delete_backups_by_session_ids.return_value = 2

        action = SessionsDeleteBackupAction(
            session_management_service=mock_service, validated_request=request
        )
        result = action.execute()

        assert result["deleted_count"] == 2
        assert result["total_requested"] == 2
        assert "Successfully deleted 2 out of 2" in result["message"]
        mock_service.delete_backups_by_session_ids.assert_called_once_with(session_ids)

    def test_execute_with_file_paths(self, mock_service: MagicMock):
        """Test execute method with file_paths."""
        file_paths = ["path/to/backup1", "path/to/backup2"]
        request = DeleteBackupRequest(file_paths=file_paths)
        mock_service.delete_backup_files.return_value = 1

        action = SessionsDeleteBackupAction(
            session_management_service=mock_service, validated_request=request
        )
        result = action.execute()

        assert result["deleted_count"] == 1
        assert result["total_requested"] == 2
        assert "Successfully deleted 1 out of 2" in result["message"]
        mock_service.delete_backup_files.assert_called_once_with(file_paths)

    def test_execute_raises_value_error_if_no_request(self, mock_service: MagicMock):
        """Test that execute raises ValueError if validated_request is missing."""
        action = SessionsDeleteBackupAction(session_management_service=mock_service)

        with pytest.raises(ValueError, match="Request is required"):
            action.execute()
