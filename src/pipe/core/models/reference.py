from pydantic import BaseModel

class Reference(BaseModel):
    path: str
    disabled: bool
