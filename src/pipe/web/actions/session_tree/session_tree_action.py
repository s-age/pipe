"""Session tree action."""

from typing import TypedDict, cast

from pipe.web.actions.base_action import BaseAction


class SessionTreeNode(TypedDict):
    """A node in the session tree."""

    session_id: str
    overview: dict  # Session metadata
    children: list["SessionTreeNode"]


class SessionTreeResponse(TypedDict):
    """Response containing session tree data."""

    sessions: dict[str, dict]  # Map of session_id to metadata
    session_tree: list[SessionTreeNode]


class SessionTreeAction(BaseAction):
    """Action for getting session tree data."""

    def execute(self) -> SessionTreeResponse:
        """Execute the session tree retrieval.

        Returns:
            Dictionary with sessions and session_tree
        """
        from pipe.web.service_container import get_session_tree_service

        tree_data = get_session_tree_service().get_session_tree()

        return cast(SessionTreeResponse, tree_data)
