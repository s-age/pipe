from typing import Any

from pydantic import BaseModel


class PromptCurrentTask(BaseModel):
    type: str
    instruction: str | None = None
    response: Any | None = None
    name: str | None = None
    content: str | None = None
    original_turns_range: list[int] | None = None
    timestamp: str
