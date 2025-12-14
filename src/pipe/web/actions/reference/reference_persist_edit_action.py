"""Reference persist edit action."""

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_reference_persist import (
    EditReferencePersistRequest,
)


class ReferencePersistEditAction(BaseAction):
    request_model = EditReferencePersistRequest

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_session_reference_service

        request = self.validated_request

        get_session_reference_service().update_reference_persist_by_index(
            request.session_id, request.reference_index, request.persist
        )

        return SuccessMessageResponse(message="Reference persist updated successfully")
