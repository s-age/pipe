from typing import TypedDict

from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.edit_hyperparameters import EditHyperparametersRequest
from pipe.web.requests.sessions.edit_multi_step_reasoning import (
    EditMultiStepReasoningRequest,
)
from pipe.web.requests.sessions.edit_session_meta import EditSessionMetaRequest
from pipe.web.requests.sessions.edit_todos import EditTodosRequest


class SessionWithMessage(TypedDict):
    """Response containing a message and full session data."""

    message: str
    session: dict  # SessionData from session.to_dict()


class SessionMetaEditAction(BaseAction):
    request_model = EditSessionMetaRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        request = self.validated_request

        try:
            get_session_service().edit_session_meta(
                request.session_id,
                request.model_dump(exclude_unset=True, exclude={"session_id"}),
            )
            return {"message": f"Session {request.session_id} metadata updated."}
        except FileNotFoundError:
            raise NotFoundError("Session not found.")


class HyperparametersEditAction(BaseAction):
    request_model = EditHyperparametersRequest

    def execute(self) -> SessionWithMessage:
        from pipe.web.service_container import get_session_service

        request = self.validated_request

        # Get current session to merge with existing hyperparameters
        session = get_session_service().get_session(request.session_id)
        if not session:
            raise NotFoundError("Session not found.")

        # Merge new values with existing hyperparameters
        current_hp = session.hyperparameters
        new_values = request.model_dump(exclude_unset=True, exclude={"session_id"})

        if current_hp:
            # Update only the fields that were provided
            merged_hp = {
                "temperature": new_values.get("temperature", current_hp.temperature),
                "top_p": new_values.get("top_p", current_hp.top_p),
                "top_k": new_values.get("top_k", current_hp.top_k),
            }
        else:
            merged_hp = new_values

        try:
            get_session_service().edit_session_meta(
                request.session_id, {"hyperparameters": merged_hp}
            )
        except FileNotFoundError:
            raise NotFoundError("Session not found.")

        # Reload session to get updated values
        session = get_session_service().get_session(request.session_id)
        if not session:
            raise NotFoundError("Session not found.")

        return {
            "message": f"Session {request.session_id} hyperparameters updated.",
            "session": session.to_dict(),
        }


class MultiStepReasoningEditAction(BaseAction):
    request_model = EditMultiStepReasoningRequest

    def execute(self) -> SessionWithMessage:
        from pipe.web.service_container import get_session_service

        request = self.validated_request

        try:
            get_session_service().edit_session_meta(
                request.session_id,
                {"multi_step_reasoning_enabled": request.multi_step_reasoning_enabled},
            )
        except FileNotFoundError:
            raise NotFoundError("Session not found.")

        session = get_session_service().get_session(request.session_id)
        if not session:
            raise NotFoundError("Session not found.")

        return {
            "message": f"Session {request.session_id} multi-step reasoning updated.",
            "session": session.to_dict(),
        }


class TodosEditAction(BaseAction):
    request_model = EditTodosRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        request = self.validated_request

        try:
            get_session_service().update_todos(request.session_id, request.todos)
            return {"message": f"Session {request.session_id} todos updated."}
        except FileNotFoundError:
            raise NotFoundError("Session not found.")


class TodosDeleteAction(BaseAction):
    def execute(self) -> dict[str, str]:
        from pipe.web.exceptions import BadRequestError
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            raise BadRequestError("session_id is required")

        try:
            get_session_service().delete_todos(session_id)
            return {"message": f"Todos deleted from session {session_id}."}
        except FileNotFoundError:
            raise NotFoundError("Session not found.")
