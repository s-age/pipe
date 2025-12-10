"""Session get action."""

from typing import TypedDict

from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.get_session import GetSessionRequest


class SessionData(TypedDict, total=False):
    session_id: str
    created_at: str
    purpose: str
    background: str
    roles: str
    multi_step_reasoning_enabled: bool
    token_count: int
    hyperparameters: dict | None
    references: list[dict]
    artifacts: list[str]
    procedure: str | None
    turns: list[dict]
    pools: list[dict]
    todos: list[dict]


class SessionGetAction(BaseAction):
    request_model = GetSessionRequest

    def execute(self) -> SessionData:
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        session_data = get_session_service().get_session(request.session_id)

        if session_data is None:
            raise NotFoundError(f"Session '{request.session_id}' not found")

        # Return SessionData directly (dispatcher will wrap in {success, data})
        return session_data.to_dict()
