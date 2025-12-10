"""
Pydantic model for validating the request body of the fork session API endpoint.
"""

from typing import ClassVar

from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import field_validator, model_validator


class ForkSessionRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id", "fork_index"]

    # Path parameters
    session_id: str
    fork_index: int

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)

    @field_validator("fork_index", mode="before")
    @classmethod
    def validate_fork_index(cls, v):
        """Ensure fork_index is a valid integer."""
        try:
            return int(v)
        except (ValueError, TypeError):
            raise BadRequestError("fork_index must be an integer")

    @model_validator(mode="after")
    def validate_fork_possible(self):
        """Validate that the session exists and fork_index is valid."""
        from pipe.web.service_container import get_session_service

        session_data = get_session_service().get_session(self.session_id)
        if not session_data:
            raise NotFoundError("Session not found.")

        if self.fork_index < 0 or self.fork_index >= len(session_data.turns):
            raise BadRequestError("Fork index out of range.")

        return self
