from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class ListDirectoryResult(CamelCaseModel):
    """Result of list_directory tool."""

    files: list[str] = Field(default_factory=list, description="List of file names")
    directories: list[str] = Field(
        default_factory=list, description="List of directory names"
    )
    error: str | None = Field(default=None, description="Error message if failed")
