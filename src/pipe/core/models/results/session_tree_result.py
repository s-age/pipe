"""Pydantic models for session tree service results."""

from pydantic import BaseModel, ConfigDict, Field


class SessionOverview(BaseModel):
    """Session metadata with session_id included.

    This represents SessionIndexEntry fields serialized with camelCase,
    plus the session_id field.
    """

    session_id: str = Field(description="Session identifier")
    created_at: str = Field(
        alias="createdAt", description="When the session was created"
    )
    last_updated_at: str = Field(
        alias="lastUpdatedAt", description="When the session was last modified"
    )
    purpose: str | None = Field(
        default=None, description="Brief description of the session's purpose"
    )

    model_config = ConfigDict(
        populate_by_name=True,  # Accept both snake_case and camelCase
        extra="allow",  # Allow extra fields for future extensibility
    )


class SessionTreeNode(BaseModel):
    """Represents a single node in the session tree."""

    session_id: str = Field(description="Session identifier")
    overview: SessionOverview = Field(description="Session metadata from index")
    children: list["SessionTreeNode"] = Field(
        default_factory=list, description="Child sessions"
    )

    model_config = ConfigDict(frozen=False)  # Allow modification for building tree


class SessionTreeResult(BaseModel):
    """Result of building session tree structure."""

    sessions: dict[str, SessionOverview] = Field(
        description="Map of session_id to metadata with session_id included"
    )
    session_tree: list[SessionTreeNode] = Field(
        description="List of root nodes with children"
    )

    model_config = ConfigDict(frozen=True)
