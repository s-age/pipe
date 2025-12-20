from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class FormatterToolResult(CamelCaseModel):
    """Result of a single formatting tool execution."""

    tool: str = Field(
        description="Name of the formatting tool (prettier, eslint, etc.)"
    )
    stdout: str | None = Field(
        default=None, description="Standard output from the tool"
    )
    stderr: str | None = Field(default=None, description="Standard error from the tool")
    exit_code: int | None = Field(default=None, description="Exit code of the tool")
    error: str | None = Field(
        default=None, description="Error message if tool not found"
    )
    message: str | None = Field(
        default=None, description="Status message describing the result"
    )


class TsAutoFormatCodeResult(CamelCaseModel):
    """Result of ts_auto_format_code tool."""

    formatting_results: list[FormatterToolResult] = Field(
        description="Results from each formatting tool execution"
    )
    message: str | None = Field(default=None, description="Overall status message")
