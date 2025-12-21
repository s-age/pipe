"""Result model for compress_session_turns tool."""

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class CompressSessionTurnsResult(CamelCaseModel):
    """Result from compressing session turns with a summary."""

    message: str | None = Field(
        default=None, description="Success message after compressing turns"
    )
    current_turn_count: int | None = Field(
        default=None,
        description="Current number of turns in the session after compression",
    )
    error: str | None = Field(
        default=None, description="Error message if operation failed"
    )
