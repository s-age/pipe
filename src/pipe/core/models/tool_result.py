from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ToolResult(BaseModel, Generic[T]):
    """
    Standard wrapper for all tool execution results.
    Separates successful data from error states to avoid ambiguity.
    """

    data: T | None = Field(
        default=None, description="The result data of the tool execution."
    )
    error: str | None = Field(
        default=None, description="Error message if the tool execution failed."
    )

    @property
    def is_success(self) -> bool:
        return self.error is None
