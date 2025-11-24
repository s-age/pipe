from pydantic import BaseModel


class RoleOption(BaseModel):
    label: str
    value: str
