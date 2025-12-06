"""
Pydantic model for validating the request body of the edit todos API endpoint.
"""

from typing import Any

from pipe.core.models.todo import TodoItem
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, model_validator


class EditTodosRequest(BaseModel):
    todos: list[TodoItem]

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: Any) -> Any:
        return normalize_camel_case_keys(data)
