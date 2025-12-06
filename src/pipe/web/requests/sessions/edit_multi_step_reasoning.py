"""Pydantic model for validating the edit multi-step reasoning API request body."""

from typing import Any

from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, model_validator


class EditMultiStepReasoningRequest(BaseModel):
    """Request body for toggling multi-step reasoning for a session.

    Fields:
        multi_step_reasoning_enabled: bool
    """

    multi_step_reasoning_enabled: bool

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
