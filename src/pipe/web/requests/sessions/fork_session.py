"""
Pydantic model for validating the request body of the fork session API endpoint.
"""

from typing import Any

from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, field_validator, model_validator


class ForkSessionRequest(BaseModel):
    session_id: str

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)

    @field_validator("session_id")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """Ensures the session_id is not empty."""
        if not v or not v.strip():
            raise ValueError("session_id must not be empty.")
        return v
