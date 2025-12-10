"""Pydantic model for validating the edit multi-step reasoning API request body."""

from typing import ClassVar

from pipe.web.exceptions import NotFoundError
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
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)

    @model_validator(mode="after")
    def validate_session_exists(self):
        """Validate that the session exists."""
        from pipe.web.service_container import get_session_service

        session_data = get_session_service().get_session(self.session_id)
        if not session_data:
            raise NotFoundError("Session not found.")

        return self
