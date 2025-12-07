"""
Pydantic model for validating the request body of the edit references API endpoint.
"""

from typing import Any, ClassVar

from pipe.core.models.reference import Reference
from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import model_validator


class EditReferencesRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter (from URL)
    session_id: str

    # Body field
    references: list[Reference]

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
