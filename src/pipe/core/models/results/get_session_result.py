from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class GetSessionResult(CamelCaseModel):
    """Result of get_session tool."""

    session_id: str | None = Field(default=None, description="Session ID")
    turns: list[str] = Field(
        default_factory=list, description="List of turn text representations"
    )
    turns_count: int | None = Field(default=None, description="Total number of turns")
    error: str | None = Field(default=None, description="Error message if failed")
