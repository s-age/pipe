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

        tree_data = get_session_tree_service().get_session_tree()

        # Convert the dictionary from service to Pydantic model
        return SessionTreeResponse(**tree_data)
