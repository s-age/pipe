from pydantic import BaseModel


class HyperparameterValue(BaseModel):
    value: float


class Hyperparameters(BaseModel):
    temperature: HyperparameterValue | None = None
    top_p: HyperparameterValue | None = None
    top_k: HyperparameterValue | None = None
