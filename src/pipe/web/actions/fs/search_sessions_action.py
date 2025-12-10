"""Search sessions action."""

from pipe.web.actions.base_action import BaseAction


class SearchSessionsAction(BaseAction):
    """Action that searches session files for a query and returns session_id/title."""

    body_model = None  # Will validate manually with SearchSessionsRequest

    def execute(self) -> dict[str, list[dict[str, str]]]:
        # Lazy import app-level objects to avoid circular imports
        from pipe.web.service_container import get_session_service

        request_json = {}
        if self.request_data and self.request_data.is_json:
            try:
                request_json = self.request_data.get_json(force=True)
            except Exception:
                request_json = {}

        # Validate request shape using a pydantic request model
        from pipe.web.requests.search_sessions import SearchSessionsRequest

        req = SearchSessionsRequest(**(request_json or {}))

        query = req.query.strip()

        sessions_dir = get_session_service().repository.sessions_dir

        # Delegate the search logic to the service layer for reusability
        from pipe.core.services.search_sessions_service import (
            SearchSessionsService,
        )

        svc = SearchSessionsService(sessions_dir)
        matches = svc.search(query)

        return {"results": matches}
