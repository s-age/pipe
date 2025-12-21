"""Session delete action."""

from pipe.web.action_responses import SessionDeleteResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_session import DeleteSessionRequest


class SessionDeleteAction(BaseAction):
    request_model = DeleteSessionRequest

    def execute(self) -> SessionDeleteResponse:
        from pipe.web.service_container import get_session_management_service

        request = self.validated_request

        get_session_management_service().delete_sessions([request.session_id])

        return SessionDeleteResponse(
            message="Session deleted successfully", session_id=request.session_id
        )
