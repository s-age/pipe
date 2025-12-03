"""
Pydantic model for validating the request body of the delete sessions API endpoint.
"""

from pydantic import BaseModel


class DeleteSessionsRequest(BaseModel):
    session_ids: list[str]


class DeleteBackupRequest(BaseModel):
    file_paths: list[str]
