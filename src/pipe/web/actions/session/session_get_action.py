"""Session get action."""

from pipe.core.models.session import Session
from pipe.core.services.session_service import SessionService
from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.get_session import GetSessionRequest


class SessionGetAction(BaseAction):
    """Get a session by ID.

    This action uses constructor injection for SessionService,
    following the DI pattern.
    """

    request_model = GetSessionRequest

    def __init__(
        self,
        session_service: SessionService,
        validated_request: GetSessionRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.session_service = session_service
        self.validated_request = validated_request

    def execute(self) -> Session:
        if not self.validated_request:
            raise ValueError("Request is required")

        request = self.validated_request
        session_data = self.session_service.get_session(request.session_id)

        if session_data is None:
            raise NotFoundError(f"Session '{request.session_id}' not found")

        return session_data
