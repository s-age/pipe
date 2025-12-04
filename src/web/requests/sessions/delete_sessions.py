"""
Pydantic model for validating bulk delete sessions request body.
"""

from pydantic import BaseModel, field_validator


class DeleteSessionsRequest(BaseModel):
    """
    Request model for bulk deleting sessions.

    Validates that session_ids is a non-empty list of strings.

    Attributes:
        session_ids: List of session IDs to delete

    Examples:
        # Valid request
        request = DeleteSessionsRequest(
            session_ids=["session-1", "session-2", "session-3"]
        )

        # Invalid request (empty list)
        request = DeleteSessionsRequest(
            session_ids=[]  # Raises ValueError
        )
    """

    session_ids: list[str]

    @field_validator("session_ids")
    @classmethod
    def validate_session_ids(cls, v: list[str]) -> list[str]:
        """
        Validate that session_ids is not empty and contains valid IDs.

        Args:
            v: List of session IDs

        Returns:
            Validated list

        Raises:
            ValueError: If list is empty or contains invalid IDs
        """
        if not v:
            raise ValueError("session_ids must not be empty")

        for session_id in v:
            if not session_id or not session_id.strip():
                raise ValueError("session_ids must not contain empty strings")

        return v
