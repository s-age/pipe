"""Search sessions action."""

from pipe.core.services.search_sessions_service import SearchSessionsService
from pipe.web.action_responses import SearchSessionsResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.search_sessions import SearchSessionsRequest


class SearchSessionsAction(BaseAction):
    """Search sessions by query.

    This action uses constructor injection for SearchSessionsService,
    following the DI pattern.
    """

    request_model = SearchSessionsRequest

    def __init__(
        self,
        search_sessions_service: SearchSessionsService,
        validated_request: SearchSessionsRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.search_sessions_service = search_sessions_service
        self.validated_request = validated_request

    def execute(self) -> SearchSessionsResponse:
        if not self.validated_request:
            raise ValueError("Request is required")

        request = self.validated_request

        results = self.search_sessions_service.search(request.query)

        return SearchSessionsResponse(results=results)
