from pydantic import BaseModel, Field


class Hyperparameters(BaseModel):
    temperature: float | None = None
    top_p: float | None = Field(None, alias="top_p")
    top_k: float | None = Field(None, alias="top_k")
