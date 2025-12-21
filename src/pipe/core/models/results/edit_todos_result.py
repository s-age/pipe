"""Result model for edit_todos tool."""

from __future__ import annotations

from pipe.core.models.base import CamelCaseModel
from pipe.core.models.todo import TodoItem
from pydantic import Field


class EditTodosResult(CamelCaseModel):
    """Result from editing TODO items in a session."""

    message: str | None = Field(
        default=None, description="Success message after updating todos"
    )
    current_todos: list[TodoItem] | None = Field(
        default=None, description="Current list of todos after update"
    )
    error: str | None = Field(
        default=None, description="Error message if operation failed"
    )
