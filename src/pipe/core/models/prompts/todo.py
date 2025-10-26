from pydantic import BaseModel

class PromptTodo(BaseModel):
    title: str
    description: str
    checked: bool
