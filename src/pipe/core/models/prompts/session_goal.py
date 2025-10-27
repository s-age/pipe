from pydantic import BaseModel


class PromptSessionGoal(BaseModel):
    description: str
    purpose: str
    background: str
