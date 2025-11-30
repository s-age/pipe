from typing import Any

from pydantic import BaseModel, Field


class CreateTherapistRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session to diagnose")


class ApplyDoctorRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session to modify")
    modifications: dict[str, Any] = Field(
        ..., description="The approved modifications to apply"
    )
