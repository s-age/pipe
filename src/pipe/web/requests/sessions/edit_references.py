"""
Pydantic model for validating the request body of the edit references API endpoint.
"""

from typing import Any

from pipe.core.models.reference import Reference
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, model_validator


class EditReferencesRequest(BaseModel):
    references: list[Reference]

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
