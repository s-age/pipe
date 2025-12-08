"""Service for managing session todos."""

from pipe.core.domains.todos import delete_todos_in_session, update_todos_in_session
from pipe.core.models.todo import TodoItem
from pipe.core.services.session_service import SessionService


class SessionTodoService:
    """Handles all todo-related operations for sessions."""

    def __init__(self, session_service: SessionService):
        self.session_service = session_service

    def update_todos(self, session_id: str, todos: list[TodoItem]):
        """Updates session todos with typed TodoItem objects."""
        session = self.session_service._fetch_session(session_id)
        if session:
            update_todos_in_session(session, todos)
            self.session_service._save_session(session)

    def delete_todos(self, session_id: str):
        session = self.session_service._fetch_session(session_id)
        if session:
            delete_todos_in_session(session)
            self.session_service._save_session(session)
