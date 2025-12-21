"""Result model for ts_run_and_test_code tool."""

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class TsRunAndTestCodeResult(CamelCaseModel):
    """Result from running or testing TypeScript code."""

    stdout: str | None = Field(
        default=None, description="Standard output from execution"
    )
    stderr: str | None = Field(
        default=None, description="Standard error from execution"
    )
    exit_code: int | None = Field(default=None, description="Exit code from execution")
    message: str | None = Field(
        default=None, description="Status message about the execution"
    )
    error: str | None = Field(
        default=None, description="Error message if execution failed"
    )
