"""Result model for edit_todos tool."""

from typing import Any

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class EditTodosResult(CamelCaseModel):
    """Result from editing TODO items in a session."""

    message: str | None = Field(
        default=None, description="Success message after updating todos"
    )
    current_todos: list[dict[str, Any]] | None = Field(
        default=None, description="Current list of todos after update"
    )
    error: str | None = Field(
        default=None, description="Error message if operation failed"
    )
