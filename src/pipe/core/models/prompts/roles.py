from pydantic import BaseModel
from typing import List

class PromptRoles(BaseModel):
    description: str
    definitions: List[str]
