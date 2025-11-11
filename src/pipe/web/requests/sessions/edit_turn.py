"""
Pydantic model for validating the request body of the edit turn API endpoint.
"""

from typing import Any

from pydantic import BaseModel, field_validator


class EditTurnRequest(BaseModel):
    """
    Request model for editing a turn.
    Accepts partial updates with either 'content' or 'instruction' fields.
    """

    content: str | None = None
    instruction: str | None = None

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

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override to only include non-None fields in the output."""
        data = super().model_dump(**kwargs)
        return {k: v for k, v in data.items() if v is not None}
