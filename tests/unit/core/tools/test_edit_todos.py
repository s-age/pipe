"""Unit tests for edit_todos tool."""

import os
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.edit_todos_result import EditTodosResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.edit_todos import edit_todos

from tests.factories.models.todo_factory import TodoFactory


class TestEditTodos:
    """Tests for edit_todos function."""

    @pytest.fixture
    def mock_session_service(self):
        """Create a mock session service."""
        service = MagicMock()
        service.project_root = "/mock/root"
        service.settings = MagicMock()
        return service

    @pytest.fixture
    def mock_todo_service(self):
        """Create a mock todo service."""
        return MagicMock()

    @pytest.fixture
    def mock_factory(self, mock_todo_service):
        """Create a mock service factory."""
        factory = MagicMock()
        factory.create_session_todo_service.return_value = mock_todo_service
        return factory

    @patch("pipe.core.tools.edit_todos.ServiceFactory")
    def test_edit_todos_success(
        self,
        MockServiceFactory,
        mock_session_service,
        mock_todo_service,
        mock_factory,
    ):
        """Test successful TODO update."""
        # Setup
        MockServiceFactory.return_value = mock_factory
        session_id = "test-session"
        todos = TodoFactory.create_batch(2)

        mock_session = MagicMock()
        mock_session.todos = todos
        mock_session_service.get_session.return_value = mock_session

        # Execute
        result = edit_todos(
            todos=todos, session_service=mock_session_service, session_id=session_id
        )

        # Verify
        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, EditTodosResult)
        assert result.data.current_todos == todos
        assert f"successfully updated in session {session_id}" in result.data.message

        MockServiceFactory.assert_called_once_with(
            mock_session_service.project_root, mock_session_service.settings
        )
        mock_todo_service.update_todos.assert_called_once_with(session_id, todos)
        mock_session_service.get_session.assert_called_once_with(session_id)

    def test_edit_todos_missing_session_service(self):
        """Test error when session_service is missing."""
        todos = TodoFactory.create_batch(1)
        result = edit_todos(todos=todos, session_service=None)

        assert isinstance(result, ToolResult)
        assert not result.is_success
        assert "requires a session_service" in result.error

    def test_edit_todos_missing_session_id(self, mock_session_service):
        """Test error when session_id is missing and not in environment."""
        todos = TodoFactory.create_batch(1)
        with patch.dict(os.environ, {}, clear=True):
            result = edit_todos(
                todos=todos, session_service=mock_session_service, session_id=None
            )

        assert isinstance(result, ToolResult)
        assert not result.is_success
        assert "No session_id provided" in result.error

    @patch("pipe.core.tools.edit_todos.ServiceFactory")
    def test_edit_todos_use_env_session_id(
        self,
        MockServiceFactory,
        mock_session_service,
        mock_todo_service,
        mock_factory,
    ):
        """Test using session_id from environment variable."""
        # Setup
        MockServiceFactory.return_value = mock_factory
        env_session_id = "env-session-id"
        todos = TodoFactory.create_batch(1)

        mock_session = MagicMock()
        mock_session.todos = todos
        mock_session_service.get_session.return_value = mock_session

        # Execute
        with patch.dict(os.environ, {"PIPE_SESSION_ID": env_session_id}):
            result = edit_todos(
                todos=todos, session_service=mock_session_service, session_id=None
            )

        # Verify
        assert result.is_success
        mock_todo_service.update_todos.assert_called_once_with(env_session_id, todos)

    @patch("pipe.core.tools.edit_todos.ServiceFactory")
    def test_edit_todos_session_not_found(
        self,
        MockServiceFactory,
        mock_session_service,
        mock_todo_service,
        mock_factory,
    ):
        """Test error when session is not found after update."""
        # Setup
        MockServiceFactory.return_value = mock_factory
        session_id = "test-session"
        todos = TodoFactory.create_batch(1)

        mock_session_service.get_session.return_value = None

        # Execute
        result = edit_todos(
            todos=todos, session_service=mock_session_service, session_id=session_id
        )

        # Verify
        assert not result.is_success
        assert f"Session with ID {session_id} not found" in result.error

    @patch("pipe.core.tools.edit_todos.ServiceFactory")
    def test_edit_todos_exception_handling(
        self,
        MockServiceFactory,
        mock_session_service,
        mock_todo_service,
        mock_factory,
    ):
        """Test exception handling during update."""
        # Setup
        MockServiceFactory.return_value = mock_factory
        session_id = "test-session"
        todos = TodoFactory.create_batch(1)

        mock_todo_service.update_todos.side_effect = Exception("Database error")

        # Execute
        result = edit_todos(
            todos=todos, session_service=mock_session_service, session_id=session_id
        )

        # Verify
        assert not result.is_success
        assert "Failed to update todos in session: Database error" in result.error
