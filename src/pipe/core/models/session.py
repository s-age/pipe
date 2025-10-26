import os
import json
from pydantic import BaseModel, Field
from typing import Optional, List

from pipe.core.utils.file import locked_json_write
from pipe.core.models.turn import Turn
from pipe.core.models.todo import TodoItem
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.reference import Reference
from pipe.core.collections.turns import TurnCollection

class Session(BaseModel):
    """
    Represents a single user session, corresponding to a unique session file (e.g., `${session_id}.json`).
    This class is responsible for holding the detailed state of a conversation and persisting itself to a file.
    It does not manage the collection of all sessions or the index file.
    """
    session_id: str
    created_at: str
    purpose: Optional[str] = None
    background: Optional[str] = None
    roles: List[str] = []
    multi_step_reasoning_enabled: bool = False
    token_count: int = 0
    hyperparameters: Optional[Hyperparameters] = None
    references: List[Reference] = Field(default_factory=list)
    turns: TurnCollection = Field(default_factory=TurnCollection)
    pools: TurnCollection = Field(default_factory=TurnCollection)
    todos: Optional[List[TodoItem]] = None

    def save(self, session_path: str, lock_path: str):
        """Saves the session to a JSON file using a locked write utility."""
        os.makedirs(os.path.dirname(session_path), exist_ok=True)
        locked_json_write(lock_path, session_path, self.model_dump())

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the session suitable for templates."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "purpose": self.purpose,
            "background": self.background,
            "roles": self.roles,
            "multi_step_reasoning_enabled": self.multi_step_reasoning_enabled,
            "token_count": self.token_count,
            "hyperparameters": self.hyperparameters.model_dump() if self.hyperparameters else None,
            "references": [r.model_dump() for r in self.references],
            "turns": [t.model_dump() for t in self.turns],
            "pools": [p.model_dump() for p in self.pools],
            "todos": [t.model_dump() for t in self.todos] if self.todos else [],
        }
