"""Unit tests for delete_todos tool."""

import os
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.delete_todos_result import DeleteTodosResult
from pipe.core.tools.delete_todos import delete_todos

from tests.factories.models.session_factory import SessionFactory


class TestDeleteTodos:
    """Tests for delete_todos function."""

    @pytest.fixture
    def mock_session_service(self):
        """Fixture for mocked session service."""
        service = MagicMock()
        service.project_root = "/mock/project/root"
        service.settings = MagicMock()
        return service

    @pytest.fixture
    def mock_todo_service(self):
        """Fixture for mocked todo service."""
        return MagicMock()

    @patch("pipe.core.tools.delete_todos.ServiceFactory")
    def test_delete_todos_success(
        self, MockServiceFactory, mock_session_service, mock_todo_service
    ):
        """Test successful deletion of todos."""
        # Setup mocks
        session_id = "test-session-123"
        factory_instance = MockServiceFactory.return_value
        factory_instance.create_session_todo_service.return_value = mock_todo_service

        # Mock session after deletion (empty todos)
        updated_session = SessionFactory.create(session_id=session_id, todos=[])
        mock_session_service.get_session.return_value = updated_session

        # Execute
        result = delete_todos(
            session_service=mock_session_service, session_id=session_id
        )

        # Verify
        assert result.is_success
        assert isinstance(result.data, DeleteTodosResult)
        assert (
            result.data.message
            == f"Todos successfully deleted from session {session_id}."
        )
        assert result.data.current_todos == []

        mock_todo_service.delete_todos.assert_called_once_with(session_id)
        mock_session_service.get_session.assert_called_once_with(session_id)

    @patch("pipe.core.tools.delete_todos.ServiceFactory")
    def test_delete_todos_with_env_session_id(
        self, MockServiceFactory, mock_session_service, mock_todo_service
    ):
        """Test deletion using session_id from environment variable."""
        session_id = "env-session-456"
        factory_instance = MockServiceFactory.return_value
        factory_instance.create_session_todo_service.return_value = mock_todo_service

        updated_session = SessionFactory.create(session_id=session_id, todos=[])
        mock_session_service.get_session.return_value = updated_session

        with patch.dict(os.environ, {"PIPE_SESSION_ID": session_id}):
            result = delete_todos(session_service=mock_session_service)

        assert result.is_success
        mock_todo_service.delete_todos.assert_called_once_with(session_id)

    def test_delete_todos_missing_service(self):
        """Test error when session_service is missing."""
        result = delete_todos(session_service=None)
        assert not result.is_success
        assert "requires a session_service" in result.error

    def test_delete_todos_missing_session_id(self, mock_session_service):
        """Test error when session_id is missing and not in environment."""
        with patch.dict(os.environ, {}, clear=True):
            result = delete_todos(session_service=mock_session_service, session_id=None)

        assert not result.is_success
        assert "No session_id provided" in result.error

    @patch("pipe.core.tools.delete_todos.ServiceFactory")
    def test_delete_todos_session_not_found(
        self, MockServiceFactory, mock_session_service, mock_todo_service
    ):
        """Test error when session is not found after deletion."""
        session_id = "missing-session"
        factory_instance = MockServiceFactory.return_value
        factory_instance.create_session_todo_service.return_value = mock_todo_service

        mock_session_service.get_session.return_value = None

        result = delete_todos(
            session_service=mock_session_service, session_id=session_id
        )

        assert not result.is_success
        assert f"Session with ID {session_id} not found" in result.error

    @patch("pipe.core.tools.delete_todos.ServiceFactory")
    def test_delete_todos_exception_handling(
        self, MockServiceFactory, mock_session_service
    ):
        """Test error handling when an exception occurs."""
        MockServiceFactory.side_effect = Exception("Factory error")

        result = delete_todos(
            session_service=mock_session_service, session_id="test-session"
        )

        assert not result.is_success
        assert "Failed to delete todos" in result.error
        assert "Factory error" in result.error

    @patch("pipe.core.tools.delete_todos.ServiceFactory")
    def test_delete_todos_handles_none_todos(
        self, MockServiceFactory, mock_session_service, mock_todo_service
    ):
        """Test that None todos in updated session are handled as empty list."""
        session_id = "none-todos-session"
        factory_instance = MockServiceFactory.return_value
        factory_instance.create_session_todo_service.return_value = mock_todo_service

        # Mock session where todos is None
        updated_session = SessionFactory.create(session_id=session_id)
        updated_session.todos = None
        mock_session_service.get_session.return_value = updated_session

        result = delete_todos(
            session_service=mock_session_service, session_id=session_id
        )

        assert result.is_success
        assert result.data.current_todos == []
