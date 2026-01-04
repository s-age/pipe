"""Unit tests for TurnEditAction."""

from unittest.mock import MagicMock, patch

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.turn.turn_edit_action import TurnEditAction
from pipe.web.requests.sessions.edit_turn import EditTurnRequest


class TestTurnEditAction:
    """Tests for the TurnEditAction class."""

    @patch("pipe.web.service_container.get_session_turn_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test that execute calls the service with correct data and returns success."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Mock the validated request
        # We use MagicMock instead of real EditTurnRequest to avoid triggering
        # its internal validation which requires a running session service.
        mock_request = MagicMock(spec=EditTurnRequest)
        mock_request.session_id = "test-session-id"
        mock_request.turn_index = 5

        # Simulate model_dump behavior as used in the action
        mock_request.model_dump.return_value = {"content": "Updated content"}

        action = TurnEditAction(validated_request=mock_request)

        # Execute
        response = action.execute()

        # Assertions
        assert isinstance(response, SuccessMessageResponse)
        assert response.message == "Turn updated successfully"

        # Verify model_dump was called with correct parameters
        mock_request.model_dump.assert_called_once_with(
            exclude={"session_id", "turn_index"}, exclude_none=True
        )

        # Verify service was called with correct parameters
        mock_service.edit_turn.assert_called_once_with(
            "test-session-id", 5, {"content": "Updated content"}
        )

    @patch("pipe.web.service_container.get_session_turn_service")
    def test_execute_with_multiple_fields(self, mock_get_service: MagicMock) -> None:
        """Test that execute handles multiple update fields correctly."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=EditTurnRequest)
        mock_request.session_id = "session-123"
        mock_request.turn_index = 0
        mock_request.model_dump.return_value = {
            "content": "New content",
            "instruction": "New instruction",
        }

        action = TurnEditAction(validated_request=mock_request)

        # Execute
        action.execute()

        # Verify service call
        mock_service.edit_turn.assert_called_once_with(
            "session-123",
            0,
            {"content": "New content", "instruction": "New instruction"},
        )
