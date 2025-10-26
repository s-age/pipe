from pydantic import BaseModel
from typing import List, Dict, Any

class PromptConversationHistory(BaseModel):
    description: str
    turns: List[Dict[str, Any]]
