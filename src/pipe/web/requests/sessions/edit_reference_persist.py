from typing import ClassVar

from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import field_validator, model_validator


class EditReferencePersistRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id", "reference_index"]

    # Path parameters (from URL)
    session_id: str
    reference_index: int

    # Body field
    persist: bool

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)

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
