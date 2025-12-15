from pipe.core.models.base import CamelCaseModel
from pipe.core.models.role import RoleOption
from pipe.core.models.session import Session
from pipe.web.action_responses import SessionTreeNode, SettingsInfo
from pydantic import Field


class StartSessionContextResponse(CamelCaseModel):
    """Response model for start session context."""

    settings: SettingsInfo = Field(description="Application settings")
    session_tree: list[SessionTreeNode] = Field(description="Session tree structure")
    role_options: list[RoleOption] = Field(description="Available role options")
    current_session: Session | None = Field(
        default=None, description="Current session details if requested"
    )
