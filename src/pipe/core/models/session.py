from pydantic import BaseModel, Field
from typing import Optional, List

from pipe.core.models.turn import Turn
from pipe.core.models.todo import TodoItem
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.reference import Reference
from pipe.core.collections.turns import TurnCollection
from pipe.core.collections.references import ReferenceCollection

class Session(BaseModel):
    session_id: str
    created_at: str
    purpose: Optional[str] = None
    background: Optional[str] = None
    roles: List[str] = []
    multi_step_reasoning_enabled: bool = False
    token_count: int = 0
    hyperparameters: Optional[Hyperparameters] = None
    references: ReferenceCollection = Field(default_factory=ReferenceCollection)
    turns: TurnCollection = Field(default_factory=TurnCollection)
    pools: List[Turn] = []
    todos: Optional[List[TodoItem]] = None
