"""
Pydantic model for validating the request body of the send instruction API endpoint.
"""

from typing import Any

from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, field_validator, model_validator


class SendInstructionRequest(BaseModel):
    instruction: str

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)

    @field_validator("instruction")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """Ensures the instruction is not empty."""
        if not v or not v.strip():
            raise ValueError("instruction must not be empty.")
        return v
