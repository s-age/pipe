from pipe.core.models.base import CamelCaseModel


class PromptRoles(CamelCaseModel):
    description: str
    definitions: list[str]
