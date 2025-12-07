"""
Pydantic model for validating the request body of the edit turn API endpoint.
"""

from typing import ClassVar

from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import field_validator, model_validator


class EditTurnRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id", "turn_index"]

    """
    Request model for editing a turn.
    Accepts partial updates with either 'content' or 'instruction' fields.
    """

    # Path parameters (from URL)
    session_id: str
    turn_index: int

    # Body fields (optional)
    content: str | None = None
    instruction: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        """Validate that content is not empty or only whitespace if provided."""
        if value is not None:
            if not isinstance(value, str):
                raise ValueError("Content must be a string")
            if not value.strip():
                raise ValueError("Content cannot be empty or only whitespace")
        return value

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str | None) -> str | None:
        """Validate that instruction is not empty or only whitespace if provided."""
        if value is not None:
            if not isinstance(value, str):
                raise ValueError("Instruction must be a string")
            if not value.strip():
                raise ValueError("Instruction cannot be empty or only whitespace")
        return value

    def model_dump(self, **kwargs) -> dict:
        """Override to only include non-None fields in the output."""
        data = super().model_dump(**kwargs)
        return {k: v for k, v in data.items() if v is not None}
