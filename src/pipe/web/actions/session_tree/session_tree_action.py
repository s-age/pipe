"""Session tree action."""

from pipe.web.action_responses import SessionTreeResponse
from pipe.web.actions.base_action import BaseAction


class SessionTreeAction(BaseAction):
    """Action for getting session tree data."""

    def execute(self) -> SessionTreeResponse:
        """Execute the session tree retrieval.

        Returns:
            SessionTreeResponse model
        """
        from pipe.web.service_container import get_session_tree_service

        tree_result = get_session_tree_service().get_session_tree()

        # Convert SessionTreeResult to SessionTreeResponse using model_dump
        return SessionTreeResponse(**tree_result.model_dump())
