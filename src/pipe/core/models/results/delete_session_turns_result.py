from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class DeleteSessionTurnsResult(CamelCaseModel):
    """Result of delete_session_turns tool."""

    message: str | None = Field(default=None, description="Success message")
    error: str | None = Field(default=None, description="Error message if failed")
