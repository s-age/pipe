"""Search L2 action."""

from flask import Request
from pipe.core.models.file_search import SearchL2Request
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.web.actions.base_action import BaseAction


class SearchL2Action(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,  # Accept additional kwargs from dispatcher
    ):
        super().__init__(params, request_data, **kwargs)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> dict:
        request_data = self.request_data.get_json()
        request = SearchL2Request(**request_data)
        response = self.file_indexer_service.search_l2_data(
            request.current_path_list, request.query
        )
        return response.model_dump()
