from pipe.core.models.base import CamelCaseModel


class RoleOption(CamelCaseModel):
    label: str
    value: str
