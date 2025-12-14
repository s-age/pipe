from pydantic import Field
from pipe.core.models.base import CamelCaseModel


class Hyperparameters(CamelCaseModel):
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: float | None = Field(default=None, ge=0)
