from typing import List, Dict, Any
from pydantic import BaseModel, Field


class CreateTherapistRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session to diagnose")


class ApplyDoctorRequest(BaseModel):
    session_id: str = Field(..., description="The ID of the session to modify")
    modifications: Dict[str, Any] = Field(..., description="The approved modifications to apply")
