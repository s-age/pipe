from pipe.core.domains.session_optimization import SessionModifications
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, Field, model_validator


class CreateTherapistRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session to diagnose")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)


class ApplyDoctorRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session to modify")
    modifications: SessionModifications = Field(
        ..., description="The approved modifications to apply"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)
