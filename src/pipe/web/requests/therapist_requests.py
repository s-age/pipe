from typing import Any

from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, Field, model_validator


class CreateTherapistRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session to diagnose")

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)


class ApplyDoctorRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session to modify")
    modifications: dict[str, Any] = Field(
        ..., description="The approved modifications to apply"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
