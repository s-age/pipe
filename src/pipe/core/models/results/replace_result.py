from typing import Literal

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class ReplaceResult(CamelCaseModel):
    """Result of replace tool."""

    status: Literal["success", "failed", "error"] = Field(
        description="Execution result status"
    )
    message: str | None = Field(
        default=None, description="Success message or failure reason"
    )
    diff: str | None = Field(default=None, description="Diff of changes")
    error: str | None = Field(
        default=None, description="Error message if exception occurred"
    )
