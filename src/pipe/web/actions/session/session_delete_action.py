"""Session delete action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_session import DeleteSessionRequest


class SessionDeleteAction(BaseAction):
    request_model = DeleteSessionRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        get_session_service().delete_session(request.session_id)
        return {"message": f"Session {request.session_id} deleted."}
