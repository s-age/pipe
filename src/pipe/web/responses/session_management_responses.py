from pipe.core.models.base import CamelCaseModel
from pipe.web.action_responses import SessionTreeNode
from pydantic import Field


class ArchiveSession(CamelCaseModel):
    """Represents a single archived session in the dashboard."""

    session_id: str
    file_path: str
    purpose: str | None = None
    background: str | None = None
    roles: list[str] = Field(default_factory=list)
    procedure: str | None = None
    artifacts: list[str] = Field(default_factory=list)
    multi_step_reasoning_enabled: bool = False
    token_count: int = 0
    last_updated_at: str | None = None
    deleted_at: str | None = None


class DashboardResponse(CamelCaseModel):
    """Response model for session management dashboard."""

    session_tree: list[SessionTreeNode] = Field(description="Active sessions tree")
    archives: list[ArchiveSession] = Field(description="List of archived sessions")
