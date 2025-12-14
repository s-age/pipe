"""List directory action."""

from flask import Request
from pipe.web.action_responses import LsResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.fs.ls_request import LsRequest


class LsAction(BaseAction):
    request_model = LsRequest

    def __init__(
        self,
        validated_request: LsRequest | None = None,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,
    ):
        super().__init__(params, request_data, **kwargs)
        self.validated_request = validated_request

    def execute(self) -> LsResponse:
        from pipe.web.service_container import get_file_indexer_service

        if not self.validated_request:
            raise ValueError("Request is required")

        request = self.validated_request

        entries = get_file_indexer_service().get_ls_data(request.final_path_list)

        return LsResponse(entries=entries)
