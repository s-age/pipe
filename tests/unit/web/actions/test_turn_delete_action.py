"""Unit tests for TurnDeleteAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.turn.turn_delete_action import TurnDeleteAction
from pipe.web.requests.sessions.delete_turn import DeleteTurnRequest


class TestTurnDeleteAction:
    """Tests for TurnDeleteAction."""

    def test_request_model_is_set(self) -> None:
        """Test that the request_model is correctly set to DeleteTurnRequest."""
        assert TurnDeleteAction.request_model == DeleteTurnRequest

    @patch("pipe.web.service_container.get_session_turn_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of turn deletion."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Create a mock request
        mock_request = MagicMock(spec=DeleteTurnRequest)
        mock_request.session_id = "test-session"
        mock_request.turn_index = 1

        # Initialize action with validated request
        action = TurnDeleteAction(validated_request=mock_request)

        # Execute
        response = action.execute()

        # Verify
        mock_service.delete_turn.assert_called_once_with("test-session", 1)
        assert isinstance(response, SuccessMessageResponse)
        assert response.message == "Turn deleted successfully"

    @patch("pipe.web.service_container.get_session_turn_service")
    def test_execute_service_error_propagation(
        self, mock_get_service: MagicMock
    ) -> None:
        """Test that service exceptions are propagated."""
        # Setup
        mock_service = MagicMock()
        mock_service.delete_turn.side_effect = ValueError("Service error")
        mock_get_service.return_value = mock_service

        # Create a mock request with required attributes
        mock_request = MagicMock(spec=DeleteTurnRequest)
        mock_request.session_id = "test-session"
        mock_request.turn_index = 1

        action = TurnDeleteAction(validated_request=mock_request)

        # Execute and Verify
        with pytest.raises(ValueError, match="Service error"):
            action.execute()
