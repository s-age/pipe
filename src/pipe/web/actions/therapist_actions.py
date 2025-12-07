from typing import Any

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests import ApplyDoctorRequest, CreateTherapistRequest


class CreateTherapistSessionAction(BaseAction):
    body_model = CreateTherapistRequest  # Legacy pattern: no path params

    def execute(self) -> dict[str, str]:
        """Create therapist session and return session_id."""
        from pipe.web.service_container import get_session_service

        request_data = CreateTherapistRequest(**self.request_data.get_json())

        service = get_session_service()
        result = service.run_takt_for_therapist(request_data.session_id)

        return result


class ApplyDoctorModificationsAction(BaseAction):
    body_model = ApplyDoctorRequest  # Legacy pattern: no path params

    def execute(self) -> dict[str, Any]:
        """Apply doctor modifications and return result with Any due to dynamic
        modifications."""
        from pipe.web.service_container import get_session_service

        request_data = ApplyDoctorRequest(**self.request_data.get_json())

        result = get_session_service().run_takt_for_doctor(
            request_data.session_id, request_data.modifications
        )

        return result
