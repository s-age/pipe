"""
Pydantic model for validating the request body of the edit session meta API endpoint.
"""

from typing import Any

from pipe.core.models.hyperparameters import Hyperparameters
from pydantic import BaseModel, model_validator


class EditSessionMetaRequest(BaseModel):
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
    def check_at_least_one_field(cls, data: Any) -> Any:
        if not isinstance(data, dict) or not any(
            k in data
            for k in [
                "purpose",
                "background",
                "roles",
                "artifacts",
                "procedure",
                "multi_step_reasoning_enabled",
                "token_count",
                "hyperparameters",
            ]
        ):
            raise ValueError(
                "At least one of ['purpose', 'background', 'roles', 'artifacts', "
                "'procedure', 'multi_step_reasoning_enabled', 'token_count', "
                "'hyperparameters'] must be present."
            )
        return data
