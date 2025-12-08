"""Request model for getting session turns."""

from typing import ClassVar

from pipe.web.exceptions import NotFoundError
from pipe.web.requests.base_request import BaseRequest
from pydantic import Field, model_validator


class GetTurnsRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter
    session_id: str

    # Query parameter
    since: int = Field(default=0, ge=0, description="Starting index for turns")

    @model_validator(mode="after")
    def validate_session_exists(self):
        """Validate that the session exists."""
        from pipe.web.service_container import get_session_service

        session_data = get_session_service().get_session(self.session_id)
        if not session_data:
            raise NotFoundError("Session not found.")

        return self
