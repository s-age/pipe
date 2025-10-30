"""
Pydantic model for validating the request body of the edit references API endpoint.
"""

from pipe.core.models.reference import Reference
from pydantic import BaseModel


class EditReferencesRequest(BaseModel):
    references: list[Reference]
