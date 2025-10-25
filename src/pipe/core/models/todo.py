from pydantic import BaseModel

class TodoItem(BaseModel):
    title: str
    description: str
    checked: bool
