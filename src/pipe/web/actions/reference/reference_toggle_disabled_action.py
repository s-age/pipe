"""Reference toggle disabled action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.toggle_reference_disabled import (
    ToggleReferenceDisabledRequest,
)


class ReferenceToggleDisabledAction(BaseAction):
    request_model = ToggleReferenceDisabledRequest

    def execute(self) -> dict[str, bool]:
        from pipe.web.service_container import get_session_reference_service

        request = self.validated_request
        new_disabled_state = (
            get_session_reference_service().toggle_reference_disabled_by_index(
                request.session_id, request.reference_index
            )
        )

        return {
            "disabled": new_disabled_state,
        }
