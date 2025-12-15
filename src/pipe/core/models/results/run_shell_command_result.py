from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class RunShellCommandResult(CamelCaseModel):
    """Result of run_shell_command tool."""

    command: str | None = Field(default=None, description="Executed command")
    directory: str | None = Field(default=None, description="Execution directory")
    stdout: str | None = Field(default=None, description="Standard output")
    stderr: str | None = Field(default=None, description="Standard error")
    exit_code: int | None = Field(default=None, description="Exit code")
    error: str | None = Field(default=None, description="Error message")
    signal: str | None = Field(default="(none)", description="Signal information")
    background_pids: str | None = Field(default="(none)", description="Background PIDs")
    process_group_pgid: str | None = Field(
        default="(none)", description="Process Group PGID"
    )
