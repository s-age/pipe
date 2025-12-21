from pipe.core.models.base import CamelCaseModel
from pydantic import Field


class PromptFileReference(CamelCaseModel):
    path: str = Field(..., alias="path")
    content: str
