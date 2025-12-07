"""Pydantic model for validating the edit multi-step reasoning API request body."""

from typing import Any, ClassVar

from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import model_validator


class EditMultiStepReasoningRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter (from URL)
    session_id: str

    """Request body for toggling multi-step reasoning for a session.

    Fields:
        multi_step_reasoning_enabled: bool
    """

    # Body field
    multi_step_reasoning_enabled: bool

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
