"""
Pydantic model for validating the request body of the edit turn API endpoint.
"""
from pydantic import BaseModel
from pipe.core.models.turn import Turn

class EditTurnRequest(BaseModel):
    turn: Turn