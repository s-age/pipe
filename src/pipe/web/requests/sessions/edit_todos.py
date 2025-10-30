"""
Pydantic model for validating the request body of the edit todos API endpoint.
"""

from pipe.core.models.todo import TodoItem
from pydantic import BaseModel


class EditTodosRequest(BaseModel):
    todos: list[TodoItem]
