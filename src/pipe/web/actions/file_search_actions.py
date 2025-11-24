from flask import Request
from pipe.core.models.file_search import LsRequest, SearchL2Request
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.web.actions.base_action import BaseAction


class SearchL2Action(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict,
        request_data: Request | None = None,
    ):
        super().__init__(params, request_data)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> tuple[dict, int]:
        try:
            request_data = self.request_data.get_json()
            request = SearchL2Request(**request_data)
            response = self.file_indexer_service.search_l2_data(
                request.current_path_list, request.query
            )
            return response.model_dump(), 200
        except Exception as e:
            return {"error": str(e)}, 400


class LsAction(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict,
        request_data: Request | None = None,
    ):
        super().__init__(params, request_data)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> tuple[dict, int]:
        try:
            request_data = self.request_data.get_json()
            request = LsRequest(**request_data)
            response_entries = self.file_indexer_service.get_ls_data(
                request.final_path_list
            )
            # LsResponseモデルに適合させるためにリストをラップ
            from pipe.core.models.file_search import LsResponse

            response = LsResponse(entries=response_entries)
            return response.model_dump(), 200
        except Exception as e:
            return {"error": str(e)}, 400


class IndexFilesAction(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict,
        request_data: Request | None = None,
    ):
        super().__init__(params, request_data)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> tuple[dict, int]:
        try:
            self.file_indexer_service.create_index()
            return {"message": "Index created successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500
