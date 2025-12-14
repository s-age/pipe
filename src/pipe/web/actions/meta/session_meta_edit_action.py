"""Session meta edit action."""

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_session_meta import EditSessionMetaRequest


class SessionMetaEditAction(BaseAction):
    request_model = EditSessionMetaRequest

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_session_meta_service

        request = self.validated_request

        updates = request.model_dump(exclude={"session_id"}, exclude_unset=True)

        get_session_meta_service().edit_session_meta(request.session_id, updates)

        return SuccessMessageResponse(message="Session metadata updated successfully")
