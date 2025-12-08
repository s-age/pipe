"""Request model for deleting a turn."""

from typing import ClassVar

from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.base_request import BaseRequest
from pydantic import field_validator, model_validator


class DeleteTurnRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id", "turn_index"]

    # Path parameters
    session_id: str
    turn_index: int

    @field_validator("turn_index", mode="before")
    @classmethod
    def validate_turn_index(cls, v):
        """Ensure turn_index is a valid integer."""
        try:
            return int(v)
        except (ValueError, TypeError):
            raise BadRequestError("turn_index must be an integer")

    @model_validator(mode="after")
    def validate_turn_exists(self):
        """Validate that the session and turn exist."""
        from pipe.web.service_container import get_session_service

        session_data = get_session_service().get_session(self.session_id)
        if not session_data:
            raise NotFoundError("Session not found.")

        if self.turn_index < 0 or self.turn_index >= len(session_data.turns):
            raise BadRequestError("Turn index out of range.")

        return self
