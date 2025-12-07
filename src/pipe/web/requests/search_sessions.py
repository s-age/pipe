"""Pydantic request model for the search sessions endpoint."""

from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, field_validator, model_validator


class SearchSessionsRequest(BaseModel):
    query: str

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, data: dict | list) -> dict | list:
        return normalize_camel_case_keys(data)

    @field_validator("query")
    @classmethod
    def check_not_empty(cls, v: str):
        if not v or not str(v).strip():
            raise ValueError("query is required and must not be empty")
        return v
