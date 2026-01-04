"""Unit tests for SessionDeleteAction."""

from unittest.mock import MagicMock, patch

from pipe.web.action_responses import SessionDeleteResponse
from pipe.web.actions.session.session_delete_action import SessionDeleteAction
from pipe.web.requests.sessions.delete_session import DeleteSessionRequest


class TestSessionDeleteAction:
    """Tests for SessionDeleteAction."""

    @patch("pipe.web.service_container.get_session_management_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of session deletion.

        Verifies that the session management service is called with the correct
        session ID and that a success response is returned.
        """
        # Setup
        session_id = "test-session-123"
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Create a validated request
        request = DeleteSessionRequest(session_id=session_id)

        # Initialize action with the validated request
        action = SessionDeleteAction(validated_request=request)

        # Execute
        result = action.execute()

        # Verify
        # Ensure delete_sessions was called with the list containing the session_id
        mock_service.delete_sessions.assert_called_once_with([session_id])

        # Verify response content
        assert isinstance(result, SessionDeleteResponse)
        assert result.message == "Session deleted successfully"
        assert result.session_id == session_id
