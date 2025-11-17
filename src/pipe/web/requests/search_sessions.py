"""Pydantic request model for the search sessions endpoint."""

from pydantic import BaseModel, field_validator


class SearchSessionsRequest(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def check_not_empty(cls, v: str):
        if not v or not str(v).strip():
            raise ValueError("query is required and must not be empty")
        return v
