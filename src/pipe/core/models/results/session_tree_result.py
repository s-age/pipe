"""Pydantic models for session tree service results."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SessionTreeNode(BaseModel):
    """Represents a single node in the session tree."""

    session_id: str = Field(description="Session identifier")
    overview: dict[str, Any] = Field(description="Session metadata from index")
    children: list["SessionTreeNode"] = Field(
        default_factory=list, description="Child sessions"
    )

    model_config = ConfigDict(frozen=False)  # Allow modification for building tree


class SessionTreeResult(BaseModel):
    """Result of building session tree structure."""

    sessions: dict[str, dict[str, Any]] = Field(
        description="Map of session_id to metadata with session_id included"
    )
    session_tree: list[SessionTreeNode] = Field(
        description="List of root nodes with children"
    )

    model_config = ConfigDict(frozen=True)
