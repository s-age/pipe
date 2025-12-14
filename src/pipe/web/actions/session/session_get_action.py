"""Session get action."""

from pipe.core.models.session import Session
from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.get_session import GetSessionRequest


class SessionGetAction(BaseAction):
    request_model = GetSessionRequest

    def execute(self) -> Session:
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        session_data = get_session_service().get_session(request.session_id)

        if session_data is None:
            raise NotFoundError(f"Session '{request.session_id}' not found")

        return session_data
