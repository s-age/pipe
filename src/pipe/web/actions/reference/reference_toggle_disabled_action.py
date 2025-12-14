"""Reference toggle disabled action."""

from pipe.web.action_responses import ReferenceToggleResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.toggle_reference_disabled import (
    ToggleReferenceDisabledRequest,
)


class ReferenceToggleDisabledAction(BaseAction):
    request_model = ToggleReferenceDisabledRequest

    def execute(self) -> ReferenceToggleResponse:
        from pipe.web.service_container import (
            get_session_reference_service,
            get_session_service,
        )

        request = self.validated_request

        new_state = get_session_reference_service().toggle_reference_disabled_by_index(
            request.session_id, request.reference_index
        )

        # Fetch session to get the path for the response
        session = get_session_service().get_session(request.session_id)
        path = ""
        if session and 0 <= request.reference_index < len(session.references):
            path = session.references[request.reference_index].path

        return ReferenceToggleResponse(
            path=path,
            disabled=new_state,
            message="Reference disabled status toggled",
        )
