"""Unit tests for SessionForkAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.action_responses import SessionForkResponse
from pipe.web.actions.turn.session_fork_action import SessionForkAction
from pipe.web.exceptions import InternalServerError, NotFoundError


class TestSessionForkAction:
    """Tests for SessionForkAction.execute method."""

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.web.service_container.get_session_workflow_service")
    def test_execute_success(self, mock_get_workflow_service, mock_get_session_service):
        """Test successful session fork."""
        # Setup mocks
        mock_session_service = MagicMock()
        mock_get_session_service.return_value = mock_session_service
        mock_session_service.get_session.return_value = MagicMock()  # Session exists

        mock_workflow_service = MagicMock()
        mock_get_workflow_service.return_value = mock_workflow_service
        mock_workflow_service.fork_session.return_value = "new-session-id"

        # Setup request
        mock_request = MagicMock()
        mock_request.session_id = "old-session-id"
        mock_request.fork_index = 5

        action = SessionForkAction(validated_request=mock_request)

        # Execute
        response = action.execute()

        # Verify
        assert isinstance(response, SessionForkResponse)
        assert response.new_session_id == "new-session-id"
        mock_session_service.get_session.assert_called_once_with("old-session-id")
        mock_workflow_service.fork_session.assert_called_once_with("old-session-id", 5)

    @patch("pipe.web.service_container.get_session_service")
    def test_execute_session_not_found(self, mock_get_session_service):
        """Test execute when session is not found."""
        # Setup mocks
        mock_session_service = MagicMock()
        mock_get_session_service.return_value = mock_session_service
        mock_session_service.get_session.return_value = None  # Session not found

        # Setup request
        mock_request = MagicMock()
        mock_request.session_id = "non-existent-id"

        action = SessionForkAction(validated_request=mock_request)

        # Execute and Verify
        with pytest.raises(NotFoundError, match="Session 'non-existent-id' not found"):
            action.execute()

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.web.service_container.get_session_workflow_service")
    def test_execute_fork_failed(
        self, mock_get_workflow_service, mock_get_session_service
    ):
        """Test execute when fork_session returns None."""
        # Setup mocks
        mock_session_service = MagicMock()
        mock_get_session_service.return_value = mock_session_service
        mock_session_service.get_session.return_value = MagicMock()  # Session exists

        mock_workflow_service = MagicMock()
        mock_get_workflow_service.return_value = mock_workflow_service
        mock_workflow_service.fork_session.return_value = None  # Fork failed

        # Setup request
        mock_request = MagicMock()
        mock_request.session_id = "old-session-id"
        mock_request.fork_index = 5

        action = SessionForkAction(validated_request=mock_request)

        # Execute and Verify
        with pytest.raises(InternalServerError, match="Failed to fork session."):
            action.execute()
