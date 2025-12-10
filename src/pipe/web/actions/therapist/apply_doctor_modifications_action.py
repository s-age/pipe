"""Apply doctor modifications action."""

from pipe.core.services.session_optimization_service import DoctorResultResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests import ApplyDoctorRequest


class ApplyDoctorModificationsAction(BaseAction):
    body_model = ApplyDoctorRequest  # Legacy pattern: no path params

    def execute(self) -> tuple[DoctorResultResponse, int]:
        """Apply doctor modifications and return result."""
        from pipe.web.service_container import get_session_workflow_service

        request_data = ApplyDoctorRequest(**self.request_data.get_json())

        result = get_session_workflow_service().run_takt_for_doctor(
            request_data.session_id, request_data.modifications
        )

        return result, 200
