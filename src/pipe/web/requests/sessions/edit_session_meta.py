"""
Pydantic model for validating the request body of the edit session meta API endpoint.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, model_validator
from pipe.core.models.hyperparameters import Hyperparameters


class EditSessionMetaRequest(BaseModel):
    purpose: Optional[str] = None
    background: Optional[str] = None
    roles: Optional[List[str]] = None
    multi_step_reasoning_enabled: Optional[bool] = None
    token_count: Optional[int] = None
    hyperparameters: Optional[Hyperparameters] = None

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_field(cls, data: Any) -> Any:
        if not isinstance(data, dict) or not any(
            k in data
            for k in [
                "purpose",
                "background",
                "roles",
                "multi_step_reasoning_enabled",
                "token_count",
                "hyperparameters",
            ]
        ):
            raise ValueError(
                "At least one of ['purpose', 'background', 'roles', "
                "'multi_step_reasoning_enabled', 'token_count', 'hyperparameters'] "
                "must be present."
            )
        return data