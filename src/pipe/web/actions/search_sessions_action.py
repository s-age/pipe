"""Search sessions by grepping session files under the sessions directory."""
from typing import Any

from pipe.web.actions.base_action import BaseAction


class SearchSessionsAction(BaseAction):
    """Action that searches session files for a query and returns session_id/title."""

    def execute(self) -> tuple[dict[str, Any], int]:
        try:
            # Lazy import app-level objects to avoid circular imports
            from pipe.web.app import session_service

            request_json = {}
            if self.request_data and self.request_data.is_json:
                try:
                    request_json = self.request_data.get_json(force=True)
                except Exception:
                    request_json = {}

            # Validate request shape using a pydantic request model
            from pipe.web.requests.search_sessions import SearchSessionsRequest
            from pydantic import ValidationError

            try:
                req = SearchSessionsRequest(**(request_json or {}))
            except ValidationError as ve:
                # Return 400 with validation errors (client mistake)
                return {"message": str(ve), "errors": ve.errors()}, 400

            query = req.query.strip()

            sessions_dir = session_service.repository.sessions_dir

            # Delegate the search logic to the service layer for reusability
            from pipe.core.services.search_sessions_service import (
                SearchSessionsService,
            )

            svc = SearchSessionsService(sessions_dir)
            matches = svc.search(query)

            return {"results": matches}, 200
        except Exception as e:
            return {"message": str(e)}, 500
