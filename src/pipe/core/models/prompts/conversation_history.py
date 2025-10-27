from typing import Any

from pydantic import BaseModel


class PromptConversationHistory(BaseModel):
    description: str
    turns: list[dict[str, Any]]
