"""Result model for py_generate_code tool."""

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class PyGenerateCodeResult(CamelCaseModel):
    """Result from generating Python code."""

    generated_code: str | None = Field(
        default=None, description="The generated Python code"
    )
    error: str | None = Field(
        default=None, description="Error message if code generation failed"
    )
