from pipe.core.models.base import CamelCaseModel


class PromptTodo(CamelCaseModel):
    title: str
    description: str
    checked: bool
