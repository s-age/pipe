"""Request model for stopping a running session."""

from typing import ClassVar

from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import model_validator


class StopSessionRequest(BaseRequest):
    """
    Validates the request to stop a running session.

    Path Parameters:
    - session_id: Session identifier

    Validations:
    - Session must exist
    - Session must be currently running
    """

    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter
    session_id: str

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        """Normalize camelCase keys to snake_case."""
        return normalize_camel_case_keys(data)

    @model_validator(mode="after")
    def validate_session_running(self):
        """Validate that the session exists and is currently running."""
        from pipe.core.services.process_manager_service import ProcessManagerService
        from pipe.web.service_container import get_session_service

        session_service = get_session_service()
        session_data = session_service.get_session(self.session_id)

        if not session_data:
            raise NotFoundError(f"Session '{self.session_id}' not found.")

        # Check if process is running
        process_manager = ProcessManagerService(session_service.project_root)
        if not process_manager.is_running(self.session_id):
            raise BadRequestError(
                f"Session '{self.session_id}' is not currently running."
            )

        return self
