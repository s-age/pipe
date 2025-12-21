from pipe.core.models.base import CamelCaseModel


class Reference(CamelCaseModel):
    path: str
    disabled: bool = False
    ttl: int | None = None
    persist: bool = False
