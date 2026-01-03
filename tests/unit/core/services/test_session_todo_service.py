"""Unit tests for SessionTodoService."""

from unittest.mock import Mock, patch

import pytest
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_todo_service import SessionTodoService

from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.todo_factory import TodoFactory


@pytest.fixture
def mock_repository() -> Mock:
    """Create a mock SessionRepository."""
    return Mock(spec=SessionRepository)


@pytest.fixture
def service(mock_repository: Mock) -> SessionTodoService:
    """Create a SessionTodoService instance with mocked dependencies."""
    return SessionTodoService(repository=mock_repository)


class TestSessionTodoServiceUpdateTodos:
    """Tests for SessionTodoService.update_todos method."""

    @patch("pipe.core.services.session_todo_service.update_todos_in_session")
    def test_update_todos_success(
        self,
        mock_update_domain: Mock,
        service: SessionTodoService,
        mock_repository: Mock,
    ) -> None:
        """Test updating todos when session exists."""
        # Arrange
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        todos = TodoFactory.create_batch(2)
        mock_repository.find.return_value = session

        # Act
        service.update_todos(session_id, todos)

        # Assert
        mock_repository.find.assert_called_once_with(session_id)
        mock_update_domain.assert_called_once_with(session, todos)
        mock_repository.save.assert_called_once_with(session)

    @patch("pipe.core.services.session_todo_service.update_todos_in_session")
    def test_update_todos_session_not_found(
        self,
        mock_update_domain: Mock,
        service: SessionTodoService,
        mock_repository: Mock,
    ) -> None:
        """Test updating todos when session does not exist."""
        # Arrange
        session_id = "non-existent"
        todos = TodoFactory.create_batch(2)
        mock_repository.find.return_value = None

        # Act
        service.update_todos(session_id, todos)

        # Assert
        mock_repository.find.assert_called_once_with(session_id)
        mock_update_domain.assert_not_called()
        mock_repository.save.assert_not_called()


class TestSessionTodoServiceDeleteTodos:
    """Tests for SessionTodoService.delete_todos method."""

    @patch("pipe.core.services.session_todo_service.delete_todos_in_session")
    def test_delete_todos_success(
        self,
        mock_delete_domain: Mock,
        service: SessionTodoService,
        mock_repository: Mock,
    ) -> None:
        """Test deleting todos when session exists."""
        # Arrange
        session_id = "test-session"
        session = SessionFactory.create(session_id=session_id)
        mock_repository.find.return_value = session

        # Act
        service.delete_todos(session_id)

        # Assert
        mock_repository.find.assert_called_once_with(session_id)
        mock_delete_domain.assert_called_once_with(session)
        mock_repository.save.assert_called_once_with(session)

    @patch("pipe.core.services.session_todo_service.delete_todos_in_session")
    def test_delete_todos_session_not_found(
        self,
        mock_delete_domain: Mock,
        service: SessionTodoService,
        mock_repository: Mock,
    ) -> None:
        """Test deleting todos when session does not exist."""
        # Arrange
        session_id = "non-existent"
        mock_repository.find.return_value = None

        # Act
        service.delete_todos(session_id)

        # Assert
        mock_repository.find.assert_called_once_with(session_id)
        mock_delete_domain.assert_not_called()
        mock_repository.save.assert_not_called()
