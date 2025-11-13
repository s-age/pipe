from pydantic import BaseModel


class ProcedureOption(BaseModel):
    label: str
    value: str
