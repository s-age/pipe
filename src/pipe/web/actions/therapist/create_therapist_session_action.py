"""Create therapist session action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests import CreateTherapistRequest


class CreateTherapistSessionAction(BaseAction):
    body_model = CreateTherapistRequest  # Legacy pattern: no path params

    def execute(self) -> dict[str, str]:
        """Create therapist session and return session_id."""
        from pipe.web.service_container import get_session_workflow_service

        request_data = CreateTherapistRequest(**self.request_data.get_json())

        result = get_session_workflow_service().run_takt_for_therapist(
            request_data.session_id
        )

        return result
