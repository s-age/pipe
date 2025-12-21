"""Search L2 action."""

from flask import Request
from pipe.core.models.file_search import SearchL2Response
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.fs.search_l2_request import SearchL2Request


class SearchL2Action(BaseAction):
    request_model = SearchL2Request

    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        validated_request: SearchL2Request | None = None,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,
    ):
        super().__init__(params, request_data, **kwargs)
        self.file_indexer_service = file_indexer_service
        self.validated_request = validated_request

    def execute(self) -> SearchL2Response:
        if not self.validated_request:
            raise ValueError("Request is required")

        response = self.file_indexer_service.search_l2_data(
            self.validated_request.current_path_list, self.validated_request.query
        )
        return response
