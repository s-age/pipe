"""
Pydantic model for validating the request body of the send instruction API endpoint.
"""
from pydantic import BaseModel, field_validator

class SendInstructionRequest(BaseModel):
    instruction: str

    @field_validator('instruction')
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """Ensures the instruction is not empty."""
        if not v or not v.strip():
            raise ValueError("instruction must not be empty.")
        return v
