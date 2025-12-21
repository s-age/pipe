from pipe.core.models.session_optimization import SessionModifications
from pipe.web.requests.base_request import BaseRequest
from pydantic import Field


class CreateTherapistRequest(BaseRequest):
    session_id: str = Field(..., description="The ID of the session to diagnose")


class ApplyDoctorRequest(BaseRequest):
    session_id: str = Field(..., description="The ID of the session to modify")
    modifications: SessionModifications = Field(
        ..., description="The approved modifications to apply"
    )
