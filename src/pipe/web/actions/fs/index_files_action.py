"""Index files action."""

from flask import Request
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.web.actions.base_action import BaseAction


class IndexFilesAction(BaseAction):
    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,  # Accept additional kwargs from dispatcher
    ):
        super().__init__(params, request_data, **kwargs)
        self.file_indexer_service = file_indexer_service

    def execute(self) -> dict[str, str]:
        self.file_indexer_service.create_index()
        return {"message": "Index created successfully"}
