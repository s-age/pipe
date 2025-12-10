"""Todos delete action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_todos import DeleteTodosRequest


class TodosDeleteAction(BaseAction):
    request_model = DeleteTodosRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_todo_service

        request = self.validated_request
        get_session_todo_service().delete_todos(request.session_id)
        return {"message": f"Todos deleted from session {request.session_id}."}
