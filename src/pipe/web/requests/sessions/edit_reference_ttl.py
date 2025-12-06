"""
Pydantic model for validating the request body of the edit reference TTL API endpoint.
"""

from typing import Any

from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, Field, model_validator


class EditReferenceTtlRequest(BaseModel):
    ttl: int = Field(
        ...,
        ge=0,
        description="The new time-to-live value, must be a non-negative integer.",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
