"""Hyperparameters edit action."""

from typing import TypedDict

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_hyperparameters import EditHyperparametersRequest


class SessionWithMessage(TypedDict):
    """Response containing a message and full session data."""

    message: str
    session: dict  # SessionData from session.to_dict()


class HyperparametersEditAction(BaseAction):
    request_model = EditHyperparametersRequest

    def execute(self) -> SessionWithMessage:
        from pipe.web.service_container import get_session_meta_service

        request = self.validated_request
        new_values = request.model_dump(exclude_unset=True, exclude={"session_id"})
        session = get_session_meta_service().update_hyperparameters(
            request.session_id, new_values
        )

        return {
            "message": f"Session {request.session_id} hyperparameters updated.",
            "session": session.to_api_dict(),
        }
