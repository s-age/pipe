"""List directory action."""

from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.web.action_responses import LsResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.fs.ls_request import LsRequest


class LsAction(BaseAction):
    """List directory contents.

    This action uses constructor injection for FileIndexerService,
    following the DI pattern.
    """

    request_model = LsRequest

    def __init__(
        self,
        file_indexer_service: FileIndexerService,
        validated_request: LsRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.file_indexer_service = file_indexer_service
        self.validated_request = validated_request

    def execute(self) -> LsResponse:
        if not self.validated_request:
            raise ValueError("Request is required")

        request = self.validated_request

        entries = self.file_indexer_service.get_ls_data(request.final_path_list)

        return LsResponse(entries=entries)
