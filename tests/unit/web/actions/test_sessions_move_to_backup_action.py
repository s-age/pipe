"""Unit tests for SessionsMoveToBackup action."""

from unittest.mock import MagicMock

import pytest
from pipe.core.services.session_management_service import SessionManagementService
from pipe.web.actions.session_management.sessions_move_to_backup_action import (
    SessionsMoveToBackup,
)
from pipe.web.requests.sessions.delete_sessions import DeleteSessionsRequest


class TestSessionsMoveToBackup:
    """Unit tests for SessionsMoveToBackup action."""

    @pytest.fixture
    def mock_service(self) -> MagicMock:
        """Mock SessionManagementService."""
        return MagicMock(spec=SessionManagementService)

    @pytest.fixture
    def valid_request(self) -> DeleteSessionsRequest:
        """Valid DeleteSessionsRequest."""
        return DeleteSessionsRequest(session_ids=["session-1", "session-2"])

    def test_init(
        self, mock_service: MagicMock, valid_request: DeleteSessionsRequest
    ) -> None:
        """Test initialization of SessionsMoveToBackup."""
        action = SessionsMoveToBackup(
            session_management_service=mock_service, validated_request=valid_request
        )
        assert action.session_management_service == mock_service
        assert action.validated_request == valid_request

    def test_execute_success(
        self, mock_service: MagicMock, valid_request: DeleteSessionsRequest
    ) -> None:
        """Test successful execution of moving sessions to backup."""
        # Setup
        mock_service.move_sessions_to_backup.return_value = 2
        action = SessionsMoveToBackup(
            session_management_service=mock_service, validated_request=valid_request
        )

        # Execute
        result = action.execute()

        # Verify
        mock_service.move_sessions_to_backup.assert_called_once_with(
            ["session-1", "session-2"]
        )
        assert result["moved_count"] == 2
        assert result["total_requested"] == 2
        assert "Successfully moved 2 out of 2 sessions to backup." in result["message"]

    def test_execute_partial_success(
        self, mock_service: MagicMock, valid_request: DeleteSessionsRequest
    ) -> None:
        """Test execution when only some sessions are moved to backup."""
        # Setup
        mock_service.move_sessions_to_backup.return_value = 1
        action = SessionsMoveToBackup(
            session_management_service=mock_service, validated_request=valid_request
        )

        # Execute
        result = action.execute()

        # Verify
        assert result["moved_count"] == 1
        assert result["total_requested"] == 2
        assert "Successfully moved 1 out of 2 sessions to backup." in result["message"]

    def test_execute_no_request_raises_error(self, mock_service: MagicMock) -> None:
        """Test that execute raises ValueError if validated_request is missing."""
        action = SessionsMoveToBackup(session_management_service=mock_service)

        with pytest.raises(ValueError, match="Request is required"):
            action.execute()
