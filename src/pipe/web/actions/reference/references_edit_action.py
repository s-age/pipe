"""References edit action."""

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_references import EditReferencesRequest


class ReferencesEditAction(BaseAction):
    request_model = EditReferencesRequest

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_session_reference_service

        request = self.validated_request

        get_session_reference_service().update_references(
            request.session_id, request.references
        )

        return SuccessMessageResponse(message="References updated successfully")
