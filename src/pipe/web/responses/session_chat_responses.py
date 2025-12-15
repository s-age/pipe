from pipe.core.models.base import CamelCaseModel
from pipe.core.models.session import Session
from pipe.web.action_responses import SessionOverview, SessionTreeNode, SettingsInfo
from pydantic import Field


class ChatContextResponse(CamelCaseModel):
    """Response model for chat context including session tree and current session."""

    sessions: dict[str, SessionOverview] = Field(
        description="Map of session ID to overview"
    )
    session_tree: list[SessionTreeNode] = Field(description="Hierarchical session tree")
    settings: SettingsInfo = Field(description="Current application settings")
    current_session: Session | None = Field(
        default=None, description="Current session details if requested"
    )
