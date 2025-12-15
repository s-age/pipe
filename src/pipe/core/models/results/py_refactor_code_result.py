from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class PyRefactorCodeResult(CamelCaseModel):
    """Result of py_refactor_code tool."""

    message: str = Field(description="Status message describing the refactoring result")
