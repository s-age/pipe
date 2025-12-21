"""Service for managing session todos."""

from pipe.core.domains.todos import delete_todos_in_session, update_todos_in_session
from pipe.core.models.todo import TodoItem
from pipe.core.repositories.session_repository import SessionRepository


class SessionTodoService:
    """Handles all todo-related operations for sessions."""

    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def update_todos(self, session_id: str, todos: list[TodoItem]):
        """Updates session todos with typed TodoItem objects."""
        session = self.repository.find(session_id)
        if session:
            update_todos_in_session(session, todos)
            self.repository.save(session)

    def delete_todos(self, session_id: str):
        session = self.repository.find(session_id)
        if session:
            delete_todos_in_session(session)
            self.repository.save(session)
