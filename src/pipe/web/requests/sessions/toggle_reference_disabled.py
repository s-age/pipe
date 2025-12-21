"""Request model for toggling reference disabled state."""

from typing import ClassVar

from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.base_request import BaseRequest
from pydantic import field_validator, model_validator


class ToggleReferenceDisabledRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id", "reference_index"]

    # Path parameters
    session_id: str
    reference_index: int

    @field_validator("reference_index", mode="before")
    @classmethod
    def validate_reference_index(cls, v):
        """Ensure reference_index is a valid integer."""
        try:
            return int(v)
        except (ValueError, TypeError):
            raise BadRequestError("reference_index must be an integer")

    @model_validator(mode="after")
    def validate_reference_exists(self):
        """Validate that the session and reference exist."""
        from pipe.web.service_container import get_session_service

        session_data = get_session_service().get_session(self.session_id)
        if not session_data:
            raise NotFoundError("Session not found.")

        if self.reference_index < 0 or self.reference_index >= len(
            session_data.references
        ):
            raise BadRequestError("Reference index out of range.")

        return self
