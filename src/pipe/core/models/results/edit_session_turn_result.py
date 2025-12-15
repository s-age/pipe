"""Result model for edit_session_turn tool."""

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class EditSessionTurnResult(CamelCaseModel):
    """Result from editing a turn in a session."""

    message: str | None = Field(
        default=None, description="Success message after editing the turn"
    )
    error: str | None = Field(
        default=None, description="Error message if operation failed"
    )
