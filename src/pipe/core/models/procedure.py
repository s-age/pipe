from pipe.core.models.base import CamelCaseModel


class ProcedureOption(CamelCaseModel):
    label: str
    value: str
