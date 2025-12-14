"""Process information model for session execution tracking."""

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class ProcessInfo(CamelCaseModel):
    """
    Tracks process information for a running session.

    Used for:
    - Preventing concurrent session execution
    - Process lifecycle management
    - Streaming log file tracking
    """

    session_id: str = Field(
        ..., description="Session identifier associated with this process"
    )
    pid: int = Field(..., description="Operating system process ID", gt=0)
    started_at: str = Field(
        ..., description="ISO 8601 timestamp when the process started"
    )
    instruction: str = Field(
        ..., description="User instruction that initiated this process"
    )
    log_file: str = Field(
        ...,
        description="Absolute path to the streaming log file for this process",
    )
