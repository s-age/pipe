"""Result models for ts_find_similar_code tool."""

from typing import Any

from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class SimilarCodeMatch(CamelCaseModel):
    """A similar code match result."""

    file: str = Field(description="File path where the similar code was found")
    symbol: str = Field(description="Symbol name of the similar code")
    similarity: float = Field(description="Similarity score (0.0 to 1.0)")
    snippet: str = Field(description="Code snippet of the similar code")


class TSFindSimilarCodeResult(CamelCaseModel):
    """Result from finding similar TypeScript code."""

    base_snippet: str | None = Field(
        default=None, description="Base code snippet used for comparison"
    )
    base_type_definitions: dict[str, Any] | None = Field(
        default=None,
        description="Type definitions of the base symbol (TS type system is complex)",
    )
    matches: list[SimilarCodeMatch] | None = Field(
        default=None, description="List of similar code matches"
    )
    error: str | None = Field(
        default=None, description="Error message if operation failed"
    )
