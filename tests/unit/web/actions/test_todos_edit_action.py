"""Unit tests for TodosEditAction."""

from unittest.mock import MagicMock, patch

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.meta.todos_edit_action import TodosEditAction
from pipe.web.requests.sessions.edit_todos import EditTodosRequest


class TestTodosEditAction:
    """Tests for TodosEditAction."""

    @patch("pipe.web.service_container.get_session_todo_service")
    def test_execute_success(self, mock_get_service):
        """Test successful execution of TodosEditAction.

        Verifies that the action calls the todo service with correct parameters
        and returns a success response.
        """
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Create a mock validated request
        mock_todos = [MagicMock(name="TodoItem1"), MagicMock(name="TodoItem2")]
        mock_request = MagicMock(spec=EditTodosRequest)
        mock_request.session_id = "session-123"
        mock_request.todos = mock_todos

        action = TodosEditAction(validated_request=mock_request)

        # Execute
        response = action.execute()

        # Verify
        mock_service.update_todos.assert_called_once_with("session-123", mock_todos)
        assert isinstance(response, SuccessMessageResponse)
        assert response.message == "Todos updated successfully"
