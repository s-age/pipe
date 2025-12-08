"""Ls action."""

from flask import Request
from pipe.core.models.file_search import LsRequest, LsResponse
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.web.actions.base_action import BaseAction


class LsAction(BaseAction):
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
        request = LsRequest(**request_data)
        response_entries = self.file_indexer_service.get_ls_data(
            request.final_path_list
        )
        # LsResponseモデルに適合させるためにリストをラップ
        response = LsResponse(entries=response_entries)
        return response.model_dump()
