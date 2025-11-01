from pydantic import BaseModel


class Artifact(BaseModel):
    path: str
    contents: str | None = None
