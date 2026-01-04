"""Unit tests for SessionTurnsGetAction."""

from unittest.mock import MagicMock, patch

from pipe.core.models.turn import Turn
from pipe.web.action_responses import SessionTurnsResponse
from pipe.web.actions.turn.session_turns_get_action import SessionTurnsGetAction
from pipe.web.requests.sessions.get_turns import GetTurnsRequest

from tests.factories.models.turn_factory import TurnFactory


class TestSessionTurnsGetAction:
    """Tests for SessionTurnsGetAction.execute method."""

    @patch("pipe.web.service_container.get_session_turn_service")
    def test_execute_success(self, mock_get_service):
        """Test successful execution of getting session turns."""
        # Arrange
        session_id = "test-session-123"
        mock_turns = TurnFactory.create_batch(3)

        mock_service = MagicMock()
        mock_service.get_turns.return_value = mock_turns
        mock_get_service.return_value = mock_service

        # Create a mock request
        mock_request = MagicMock(spec=GetTurnsRequest)
        mock_request.session_id = session_id

        # Instantiate action with validated_request
        action = SessionTurnsGetAction(validated_request=mock_request)

        # Act
        response = action.execute()

        # Assert
        assert isinstance(response, SessionTurnsResponse)
        assert response.turns == mock_turns
        mock_service.get_turns.assert_called_once_with(session_id)

    @patch("pipe.web.service_container.get_session_turn_service")
    def test_execute_empty_turns(self, mock_get_service):
        """Test execution when no turns are found."""
        # Arrange
        session_id = "empty-session"
        mock_turns: list[Turn] = []

        mock_service = MagicMock()
        mock_service.get_turns.return_value = mock_turns
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=GetTurnsRequest)
        mock_request.session_id = session_id

        action = SessionTurnsGetAction(validated_request=mock_request)

        # Act
        response = action.execute()

        # Assert
        assert isinstance(response, SessionTurnsResponse)
        assert response.turns == []
        mock_service.get_turns.assert_called_once_with(session_id)
