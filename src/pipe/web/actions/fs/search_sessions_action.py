"""Search sessions action."""

from flask import Request
from pipe.web.action_responses import SearchSessionsResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.search_sessions import SearchSessionsRequest


class SearchSessionsAction(BaseAction):
    request_model = SearchSessionsRequest

    def __init__(
        self,
        validated_request: SearchSessionsRequest | None = None,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,
    ):
        super().__init__(params, request_data, **kwargs)
        self.validated_request = validated_request

    def execute(self) -> SearchSessionsResponse:
        from pipe.web.service_container import get_search_sessions_service

        if not self.validated_request:
            raise ValueError("Request is required")

        request = self.validated_request

        results = get_search_sessions_service().search(request.query)

        return SearchSessionsResponse(results=results)
