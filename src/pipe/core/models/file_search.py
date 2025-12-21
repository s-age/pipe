from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class FileIndexEntry(CamelCaseModel):
    """
    Entry for a file/directory to be stored in the Whoosh index.
    """

    path: str = Field(..., description="Full path of the file")
    filename: str = Field(..., description="File or directory name")
    is_dir: bool = Field(..., description="Flag indicating if it's a directory")
    parent_path_hash: str = Field(
        ..., description="Hash of the parent directory's path"
    )
    size: int | None = Field(None, description="File size in bytes")
    last_modified: float | None = Field(
        None, description="Last modified timestamp (UNIX timestamp)"
    )


class Level1Candidate(CamelCaseModel):
    """
    First-level search candidate.
    """

    name: str = Field(..., description="File or directory name")
    is_dir: bool = Field(..., description="Flag indicating if it's a directory")
    path_segment: str = Field(..., description="Path segment")


class SearchL2Request(CamelCaseModel):
    """
    Request body for the /api/search_l2 endpoint.
    """

    current_path_list: list[str] = Field(
        ...,
        description="Current confirmed path segments (e.g., ['src', 'components'])",
    )
    query: str = Field(..., description="User's search query")


class SearchL2Response(CamelCaseModel):
    """
    Response body from the /api/search_l2 endpoint.
    """

    level_1_candidates: list[Level1Candidate] = Field(
        ..., description="List of 1st level search candidates"
    )
    level_2_prefetched: dict[str, list[Level1Candidate]] = Field(
        ..., description="2nd level prefetched data (directory name -> candidate list)"
    )


class LsRequest(CamelCaseModel):
    """
    Request body for the /api/ls endpoint.
    """

    final_path_list: list[str] = Field(
        ...,
        description="Confirmed path segments (e.g., ['src', 'components', 'Header'])",
    )


class LsEntry(CamelCaseModel):
    """
    Individual entry for the ls endpoint.
    """

    name: str = Field(..., description="File or directory name")
    is_dir: bool = Field(..., description="Flag indicating if it's a directory")
    size: int | None = Field(None, description="File size in bytes")
    last_modified: float | None = Field(
        None, description="Last modified timestamp (UNIX timestamp)"
    )
    path: str = Field(..., description="Full path of the file")


class LsResponse(CamelCaseModel):
    """
    Response body from the /api/ls endpoint.
    """

    entries: list[LsEntry] = Field(
        ..., description="List of content for the specified path"
    )


class PrefetchResult(CamelCaseModel):
    """
    Result of prefetching Level 2 candidate data.
    """

    data: dict[str, list[Level1Candidate]] = Field(
        ..., description="Mapping of directory names to their Level 1 candidates"
    )
