from __future__ import annotations

from pipe.core.models.base import CamelCaseModel
from pipe.core.models.todo import TodoItem
from pydantic import Field


class DeleteTodosResult(CamelCaseModel):
    """Result of delete_todos tool."""

    message: str | None = Field(
        default=None, description="Success message if todos deleted"
    )
    current_todos: list[TodoItem] | None = Field(
        default=None, description="List of current todos after deletion"
    )
    error: str | None = Field(default=None, description="Error message if failed")
