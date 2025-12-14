"""Create therapist session action."""

from pipe.web.action_responses import SessionStartResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.therapist_requests import CreateTherapistRequest


class CreateTherapistSessionAction(BaseAction):
    request_model = CreateTherapistRequest

    def execute(self) -> SessionStartResponse:
        from pipe.web.service_container import get_therapist_service

        request = self.validated_request

        session_id = get_therapist_service().create_therapist_session(
            request.session_id
        )

        return SessionStartResponse(session_id=session_id)
