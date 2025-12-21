from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class GlobResult(CamelCaseModel):
    """Result of glob tool."""

    content: str | None = Field(default=None, description="Matched file paths")
    error: str | None = Field(default=None, description="Error message if failed")
