"""
Pydantic model for validating the request body of the delete sessions API endpoint.
"""

from pipe.web.requests.base_request import BaseRequest
from pydantic import field_validator


class DeleteSessionsRequest(BaseRequest):
    session_ids: list[str]


class DeleteBackupRequest(BaseRequest):
    """
    Request model for deleting backup sessions.

    Either session_ids or file_paths should be provided, but not both.
    """

    session_ids: list[str] | None = None
    file_paths: list[str] | None = None

    @field_validator("session_ids", "file_paths", mode="after")
    @classmethod
    def validate_at_least_one_provided(cls, v: list[str] | None) -> list[str] | None:
        return v

    def model_post_init(self, __context: object) -> None:
        """Validate that exactly one of session_ids or file_paths is provided."""
        if not self.session_ids and not self.file_paths:
            raise ValueError("Either session_ids or file_paths must be provided")
        if self.session_ids and self.file_paths:
            raise ValueError("Cannot provide both session_ids and file_paths")
