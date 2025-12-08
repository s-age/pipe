"""
Pydantic model for validating the request body of the send instruction API endpoint.
"""

from typing import ClassVar

from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import field_validator, model_validator


class SendInstructionRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter
    session_id: str

    # Body field
    instruction: str

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)

    @field_validator("instruction")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """Ensures the instruction is not empty."""
        if not v or not v.strip():
            raise ValueError("instruction must not be empty.")
        return v

    @model_validator(mode="after")
    def validate_session_state(self):
        """Validate session exists and has capacity for new instructions."""
        from pipe.web.service_container import get_session_service

        session_service = get_session_service()
        session_data = session_service.get_session(self.session_id)

        if not session_data:
            raise NotFoundError("Session not found.")

        if session_data.pools and len(session_data.pools) >= 25:
            error_message = (
                "Too many tasks in the processing pool (limit is 25). "
                "Please wait for the current tasks to complete before "
                "adding a new one."
            )
            raise BadRequestError(error_message)

        return self
