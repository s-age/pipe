"""
Pydantic model for validating the request body of the edit artifacts API endpoint.
"""

from typing import ClassVar

from pipe.core.models.artifact import Artifact
from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import model_validator


class EditArtifactsRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter (from URL)
    session_id: str

    # Body field
    artifacts: list[Artifact]

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)
