from typing import Any

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests import ApplyDoctorRequest, CreateTherapistRequest
from pydantic import ValidationError


class CreateTherapistSessionAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        try:
            request_data = CreateTherapistRequest(**self.request_data.get_json())

            result = get_session_service().run_takt_for_therapist(request_data.session_id)

            return result, 200

        except ValidationError as e:
            return {"message": str(e)}, 422
        except Exception as e:
            return {"message": str(e)}, 500


class ApplyDoctorModificationsAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        try:
            request_data = ApplyDoctorRequest(**self.request_data.get_json())

            result = get_session_service().run_takt_for_doctor(
                request_data.session_id, request_data.modifications
            )

            return result, 200

        except ValidationError as e:
            return {"message": str(e)}, 422
        except Exception as e:
            return {"message": str(e)}, 500
