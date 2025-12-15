from typing import Literal

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class WriteFileResult(CamelCaseModel):
    """Result of write_file tool."""

    status: Literal["success", "error"] = Field(description="Execution result status")
    message: str | None = Field(
        default=None, description="Success message or error detail"
    )
    diff: str | None = Field(
        default=None, description="Diff of changes if file existed"
    )
    error: str | None = Field(default=None, description="Error message if failed")
