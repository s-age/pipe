from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class WebFetchResult(CamelCaseModel):
    """Result of web_fetch tool."""

    message: str | None = Field(
        default=None, description="Fetched content or success message"
    )
    error: str | None = Field(default=None, description="Error message if failed")
