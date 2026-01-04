"""Unit tests for TodosDeleteAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.meta.todos_delete_action import TodosDeleteAction
from pipe.web.requests.sessions.delete_todos import DeleteTodosRequest


class TestTodosDeleteAction:
    """Tests for TodosDeleteAction."""

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock DeleteTodosRequest."""
        mock = MagicMock(spec=DeleteTodosRequest)
        mock.session_id = "test-session-123"
        return mock

    @patch("pipe.web.service_container.get_session_todo_service")
    def test_execute_success(
        self, mock_get_service: MagicMock, mock_request: MagicMock
    ) -> None:
        """Test successful execution of todos deletion."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        action = TodosDeleteAction(validated_request=mock_request)

        # Execute
        response = action.execute()

        # Verify
        mock_service.delete_todos.assert_called_once_with("test-session-123")
        assert isinstance(response, SuccessMessageResponse)
        assert response.message == "Todos deleted successfully"

    @patch("pipe.web.service_container.get_session_todo_service")
    def test_execute_service_raises_error(
        self, mock_get_service: MagicMock, mock_request: MagicMock
    ) -> None:
        """Test execution when service raises an error."""
        # Setup
        mock_service = MagicMock()
        mock_service.delete_todos.side_effect = Exception("Service error")
        mock_get_service.return_value = mock_service

        action = TodosDeleteAction(validated_request=mock_request)

        # Execute & Verify
        with pytest.raises(Exception, match="Service error"):
            action.execute()

        mock_service.delete_todos.assert_called_once_with("test-session-123")
