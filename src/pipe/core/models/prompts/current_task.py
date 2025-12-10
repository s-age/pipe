from pipe.core.models.turn import TurnResponse
from pydantic import BaseModel


class PromptCurrentTask(BaseModel):
    type: str
    instruction: str | None = None
    response: str | TurnResponse | None = None
    name: str | None = None
    content: str | None = None
    original_turns_range: list[int] | None = None
    timestamp: str
