from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class SessionSearchResult(CamelCaseModel):
    """Result of a session search."""

    session_id: str = Field(description="Session ID")
    title: str = Field(description="Session title or purpose")
    path: str | None = Field(default=None, description="Path to the session file")
