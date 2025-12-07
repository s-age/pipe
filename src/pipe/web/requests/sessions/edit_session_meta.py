"""
Pydantic model for validating the request body of the edit session meta API endpoint.
"""

from typing import ClassVar

from pipe.core.models.hyperparameters import Hyperparameters
from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import model_validator


class EditSessionMetaRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter (from URL)
    session_id: str

    # Body fields (all optional)
    purpose: str | None = None
    background: str | None = None
    roles: list[str] | None = None
    artifacts: list[str] | None = None
    procedure: str | None = None
    multi_step_reasoning_enabled: bool | None = None
    token_count: int | None = None
    hyperparameters: Hyperparameters | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "EditSessionMetaRequest":
        # Check if at least one field is set
        fields_set = self.model_fields_set
        valid_fields = [
            "purpose",
            "background",
            "roles",
            "artifacts",
            "procedure",
            "multi_step_reasoning_enabled",
            "token_count",
            "hyperparameters",
        ]
        if not any(k in fields_set for k in valid_fields):
            raise ValueError(
                "At least one of ['purpose', 'background', 'roles', 'artifacts', "
                "'procedure', 'multi_step_reasoning_enabled', 'token_count', "
                "'hyperparameters'] must be present."
            )
        return self
