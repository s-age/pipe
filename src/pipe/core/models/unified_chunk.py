"""Unified chunk models for model-agnostic streaming responses."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    """Text content chunk from model response."""

    type: Literal["text"] = "text"
    content: str = Field(..., description="Text content from the model")


class ToolCallChunk(BaseModel):
    """Tool call request chunk from model response."""

    type: Literal["tool_call"] = "tool_call"
    name: str = Field(..., description="Name of the tool to call")
    args: dict[str, Any] = Field(
        default_factory=dict, description="Arguments for the tool call"
    )


class UsageMetadata(BaseModel):
    """Token usage metadata from API response."""

    prompt_token_count: int | None = Field(None, description="Tokens in the prompt")
    candidates_token_count: int | None = Field(
        None, description="Tokens in the response"
    )
    total_token_count: int | None = Field(None, description="Total tokens used")
    cached_content_token_count: int | None = Field(
        None, description="Tokens served from cache"
    )


class MetadataChunk(BaseModel):
    """Metadata chunk containing usage information."""

    type: Literal["metadata"] = "metadata"
    usage: UsageMetadata = Field(..., description="Token usage metadata")


# Union type for all possible chunk types
UnifiedChunk = TextChunk | ToolCallChunk | MetadataChunk
