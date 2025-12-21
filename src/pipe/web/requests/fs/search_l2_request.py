"""Search L2 Request Model."""

from pipe.web.requests.base_request import BaseRequest
from pydantic import Field


class SearchL2Request(BaseRequest):
    """
    Request model for the L2 file search endpoint.
    """

    current_path_list: list[str] = Field(
        ...,
        description="Current confirmed path segments (e.g., ['src', 'components'])",
    )
    query: str = Field(..., description="User's search query")
