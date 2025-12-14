from pipe.core.models.base import CamelCaseModel


class Hyperparameters(CamelCaseModel):
    temperature: float | None = None
    top_p: float | None = None
    top_k: float | None = None
