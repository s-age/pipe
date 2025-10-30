"""
Pydantic model for validating the request body of the edit todos API endpoint.
"""
from pydantic import BaseModel
from typing import List
from pipe.core.models.todo import TodoItem

class EditTodosRequest(BaseModel):
    todos: List[TodoItem]