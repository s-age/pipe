from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class ReadFileResult(CamelCaseModel):
    """Result of read_file tool."""

    content: str | None = Field(default=None, description="File content")
    message: str | None = Field(default=None, description="Informational message")
    error: str | None = Field(default=None, description="Error message if failed")
