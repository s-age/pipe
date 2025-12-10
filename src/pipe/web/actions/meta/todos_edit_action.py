"""Todos edit action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.edit_todos import EditTodosRequest


class TodosEditAction(BaseAction):
    request_model = EditTodosRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_todo_service

        request = self.validated_request

        try:
            get_session_todo_service().update_todos(request.session_id, request.todos)
            return {"message": f"Session {request.session_id} todos updated."}
        except FileNotFoundError:
            raise NotFoundError("Session not found.")
