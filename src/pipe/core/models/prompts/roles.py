from pydantic import BaseModel


class PromptRoles(BaseModel):
    description: str
    definitions: list[str]
