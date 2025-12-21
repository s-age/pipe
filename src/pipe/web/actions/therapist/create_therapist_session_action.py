"""Create therapist session action."""

from pipe.core.services.session_optimization_service import TherapistResult
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.therapist_requests import CreateTherapistRequest


class CreateTherapistSessionAction(BaseAction):
    request_model = CreateTherapistRequest

    def execute(self) -> TherapistResult:
        from pipe.web.service_container import get_session_optimization_service

        request = self.validated_request

        result = get_session_optimization_service().run_therapist(request.session_id)

        return result
