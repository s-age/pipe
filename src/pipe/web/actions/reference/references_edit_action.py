"""References edit action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.edit_references import EditReferencesRequest


class ReferencesEditAction(BaseAction):
    request_model = EditReferencesRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_reference_service

        request = self.validated_request

        try:
            get_session_reference_service().update_references(
                request.session_id, request.references
            )
            return {"message": f"Session {request.session_id} references updated."}
        except FileNotFoundError:
            raise NotFoundError("Session not found.")
