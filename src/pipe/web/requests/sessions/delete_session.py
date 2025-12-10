"""Request model for deleting a session."""

from typing import ClassVar

from pipe.web.requests.base_request import BaseRequest


class DeleteSessionRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter
    session_id: str
