"""
Pydantic model for validating the request body of the fork session API endpoint.
"""
from pydantic import BaseModel, field_validator

class ForkSessionRequest(BaseModel):
    session_id: str

    @field_validator('session_id')
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """Ensures the session_id is not empty."""
        if not v or not v.strip():
            raise ValueError("session_id must not be empty.")
        return v
