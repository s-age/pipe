"""Apply doctor modifications action."""

from pipe.core.services.session_optimization_service import DoctorResultResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests import ApplyDoctorRequest


class ApplyDoctorModificationsAction(BaseAction):
    request_model = ApplyDoctorRequest

    def execute(self) -> DoctorResultResponse:
        """Apply doctor modifications and return result."""
        from pipe.web.service_container import get_session_workflow_service

        request = self.validated_request

        result = get_session_workflow_service().run_takt_for_doctor(
            request.session_id, request.modifications
        )

        return result
