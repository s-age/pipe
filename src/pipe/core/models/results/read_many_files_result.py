from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class FileContent(CamelCaseModel):
    """Content of a single file."""

    path: str = Field(description="File path")
    content: str | None = Field(
        default=None, description="File content if read successfully"
    )
    error: str | None = Field(default=None, description="Error message if failed")


class ReadManyFilesResult(CamelCaseModel):
    """Result of read_many_files tool."""

    files: list[FileContent] = Field(
        default_factory=list, description="List of file contents"
    )
    message: str | None = Field(
        default=None, description="Informational message about the operation"
    )
    error: str | None = Field(default=None, description="Error message if failed")
