from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class FileMatchItem(CamelCaseModel):
    """A single file content match."""

    file_path: str | None = Field(
        default=None, description="Relative path to the matched file"
    )
    line_number: int | None = Field(
        default=None, description="Line number of the match"
    )
    line_content: str | None = Field(
        default=None, description="Content of the matched line"
    )
    error: str | None = Field(
        default=None, description="Error message if file read failed"
    )


class SearchFileContentResult(CamelCaseModel):
    """Result of search_file_content tool."""

    content: list[FileMatchItem] | str = Field(
        description="List of matches or error/status message"
    )
