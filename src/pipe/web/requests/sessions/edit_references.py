"""
Pydantic model for validating the request body of the edit references API endpoint.
"""
from pydantic import BaseModel
from typing import List
from pipe.core.models.reference import Reference

class EditReferencesRequest(BaseModel):
    references: List[Reference]