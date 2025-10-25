from typing import List, Optional
from pydantic import BaseModel, Field

from .hyperparameters import Hyperparameters
from .reference import Reference
from .todo import TodoItem
from .turn import Turn

class Session(BaseModel):
    session_id: str
    created_at: str
    purpose: str
    background: str
    roles: List[str]
    multi_step_reasoning_enabled: bool
    token_count: int
    hyperparameters: Hyperparameters
    references: List[Reference]
    turns: List[Turn]
    pools: List[Turn] = Field(default_factory=list)
    todos: Optional[List[TodoItem]] = None
