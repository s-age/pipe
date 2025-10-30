"""
Pydantic model for validating the request body of the edit turn API endpoint.
"""

from pipe.core.models.turn import Turn
from pydantic import BaseModel


class EditTurnRequest(BaseModel):
    turn: Turn
