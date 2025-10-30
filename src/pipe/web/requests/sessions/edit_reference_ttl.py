"""
Pydantic model for validating the request body of the edit reference TTL API endpoint.
"""
from pydantic import BaseModel, Field

class EditReferenceTtlRequest(BaseModel):
    ttl: int = Field(..., ge=0, description="The new time-to-live value, must be a non-negative integer.")
