"""Multi-step reasoning edit action."""

from typing import TypedDict

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_multi_step_reasoning import (
    EditMultiStepReasoningRequest,
)


class SessionWithMessage(TypedDict):
    """Response containing a message and full session data."""

    message: str
    session: dict  # SessionData from session.to_dict()


class MultiStepReasoningEditAction(BaseAction):
    request_model = EditMultiStepReasoningRequest

    def execute(self) -> SessionWithMessage:
        from pipe.web.service_container import (
            get_session_meta_service,
            get_session_service,
        )

        request = self.validated_request
        get_session_meta_service().edit_session_meta(
            request.session_id,
            {"multi_step_reasoning_enabled": request.multi_step_reasoning_enabled},
        )

        session = get_session_service().get_session(request.session_id)

        return {
            "message": f"Session {request.session_id} multi-step reasoning updated.",
            "session": session.to_api_dict(),
        }
