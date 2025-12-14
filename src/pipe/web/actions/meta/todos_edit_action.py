"""Todos edit action."""

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_todos import EditTodosRequest


class TodosEditAction(BaseAction):
    request_model = EditTodosRequest

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_session_todo_service

        get_session_todo_service().update_todos(
            self.validated_request.session_id, self.validated_request.todos
        )

        return SuccessMessageResponse(message="Todos updated successfully")
