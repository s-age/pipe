from pipe.core.models.base import CamelCaseModel


class Artifact(CamelCaseModel):
    path: str
    contents: str | None = None
