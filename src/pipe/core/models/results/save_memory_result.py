from typing import Literal

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class SaveMemoryResult(CamelCaseModel):
    """Result of save_memory tool."""

    status: Literal["success", "error"] = Field(description="Execution result status")
    message: str | None = Field(default=None, description="Success or error message")
