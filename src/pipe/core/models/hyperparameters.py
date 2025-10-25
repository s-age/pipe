from typing import Optional
from pydantic import BaseModel

class HyperparameterValue(BaseModel):
    value: float

class Hyperparameters(BaseModel):
    temperature: Optional[HyperparameterValue] = None
    top_p: Optional[HyperparameterValue] = None
    top_k: Optional[HyperparameterValue] = None
