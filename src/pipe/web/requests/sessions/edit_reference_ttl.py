"""
Pydantic model for validating the request body of the edit reference TTL API endpoint.
"""

from typing import Any, ClassVar

from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import Field, model_validator


class EditReferenceTtlRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id", "reference_index"]

    # Path parameters (from URL)
    session_id: str
    reference_index: int

    # Body field
    ttl: int = Field(
        ...,
        ge=0,
        description="The new time-to-live value, must be a non-negative integer.",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
