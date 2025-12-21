"""Session fork action."""

from pipe.web.action_responses import SessionForkResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import InternalServerError, NotFoundError
from pipe.web.requests.sessions.fork_session import ForkSessionRequest


class SessionForkAction(BaseAction):
    request_model = ForkSessionRequest

    def execute(self) -> SessionForkResponse:
        from pipe.web.service_container import (
            get_session_service,
            get_session_workflow_service,
        )

        request = self.validated_request

        # Verify session exists
        if not get_session_service().get_session(request.session_id):
            raise NotFoundError(f"Session '{request.session_id}' not found")

        new_session_id = get_session_workflow_service().fork_session(
            request.session_id, request.fork_index
        )

        if not new_session_id:
            raise InternalServerError("Failed to fork session.")

        return SessionForkResponse(new_session_id=new_session_id)
