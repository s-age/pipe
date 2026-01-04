"""Unit tests for SessionsDeleteAction."""

from unittest.mock import MagicMock

import pytest
from pipe.core.services.session_management_service import SessionManagementService
from pipe.web.actions.session_management.sessions_delete_action import (
    SessionsDeleteAction,
)
from pipe.web.requests.sessions.delete_sessions import DeleteSessionsRequest


class TestSessionsDeleteAction:
    """Unit tests for SessionsDeleteAction."""

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
        """Test initialization of SessionsDeleteAction."""
        action = SessionsDeleteAction(
            session_management_service=mock_service, validated_request=valid_request
        )
        assert action.session_management_service == mock_service
        assert action.validated_request == valid_request

    def test_execute_success(
        self, mock_service: MagicMock, valid_request: DeleteSessionsRequest
    ) -> None:
        """Test successful execution of session deletion."""
        # Setup
        mock_service.delete_sessions.return_value = 2
        action = SessionsDeleteAction(
            session_management_service=mock_service, validated_request=valid_request
        )

        # Execute
        result = action.execute()

        # Verify
        mock_service.delete_sessions.assert_called_once_with(["session-1", "session-2"])
        assert result["deleted_count"] == 2
        assert result["total_requested"] == 2
        assert "Successfully deleted 2 out of 2 sessions." in result["message"]

    def test_execute_partial_success(
        self, mock_service: MagicMock, valid_request: DeleteSessionsRequest
    ) -> None:
        """Test execution when only some sessions are deleted."""
        # Setup
        mock_service.delete_sessions.return_value = 1
        action = SessionsDeleteAction(
            session_management_service=mock_service, validated_request=valid_request
        )

        # Execute
        result = action.execute()

        # Verify
        assert result["deleted_count"] == 1
        assert result["total_requested"] == 2
        assert "Successfully deleted 1 out of 2 sessions." in result["message"]

    def test_execute_no_request_raises_error(self, mock_service: MagicMock) -> None:
        """Test that execute raises ValueError if validated_request is missing."""
        action = SessionsDeleteAction(session_management_service=mock_service)

        with pytest.raises(ValueError, match="Request is required"):
            action.execute()
