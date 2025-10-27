from pydantic import BaseModel, Field


class PromptFileReference(BaseModel):
    path: str = Field(..., alias="path")
    content: str
