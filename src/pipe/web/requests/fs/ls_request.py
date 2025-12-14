"""Ls Request Model."""

from pipe.web.requests.base_request import BaseRequest
from pydantic import Field


class LsRequest(BaseRequest):
    """
    Request model for the ls endpoint.
    """

    final_path_list: list[str] = Field(
        ...,
        description="Confirmed path segments (e.g., ['src', 'components', 'Header'])",
    )
