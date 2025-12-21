"""Index files action."""

from flask import Request
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction


class IndexFilesAction(BaseAction):
    def __init__(
        self,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,
    ):
        super().__init__(params, request_data, **kwargs)

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_file_indexer_service

        get_file_indexer_service().create_index()

        return SuccessMessageResponse(message="Indexing started")
