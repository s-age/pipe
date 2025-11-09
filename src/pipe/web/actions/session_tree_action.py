"""Session Tree Action for listing sessions in tree structure."""

from typing import Any

from pipe.web.actions.base_action import BaseAction


class SessionTreeAction(BaseAction):
    """Action for getting session tree data."""

    def execute(self) -> tuple[dict[str, Any], int]:
        """Execute the session tree retrieval.

        Returns:
            A tuple of (response_dict, status_code)
        """
        try:
            # Import session_service from the Flask app module
            from pipe.web.app import session_service

            sessions_collection = session_service.list_sessions()
            sorted_sessions = sessions_collection.get_sorted_by_last_updated()

            return {"sessions": sorted_sessions}, 200
        except Exception as e:
            return {"message": str(e)}, 500
