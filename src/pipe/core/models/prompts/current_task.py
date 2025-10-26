from pydantic import BaseModel
from typing import Optional, Any, List

class PromptCurrentTask(BaseModel):
    type: str
    instruction: Optional[str] = None
    response: Optional[Any] = None
    name: Optional[str] = None
    content: Optional[str] = None
    original_turns_range: Optional[List[int]] = None
    timestamp: str
