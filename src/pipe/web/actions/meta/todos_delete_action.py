"""Todos delete action."""

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_todos import DeleteTodosRequest


class TodosDeleteAction(BaseAction):
    request_model = DeleteTodosRequest

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_session_todo_service

        get_session_todo_service().delete_todos(self.validated_request.session_id)

        return SuccessMessageResponse(message="Todos deleted successfully")
