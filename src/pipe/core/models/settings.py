from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict

class HyperparameterValue(BaseModel):
    """Represents the value and description of a hyperparameter."""
    value: float
    description: str

class Parameters(BaseModel):
    """Container for model hyperparameters."""
    temperature: HyperparameterValue
    top_p: HyperparameterValue = Field(..., alias='top_p')
    top_k: HyperparameterValue = Field(..., alias='top_k')

class Settings(BaseModel):
    """Represents the application settings loaded from setting.yml."""
    model: str = "gemini-2.5-flash"
    search_model: str = "gemini-2.5-flash"
    context_limit: int = 1000000
    api_mode: str = "gemini-api"
    language: str = "English"
    yolo: bool = False
    parameters: Parameters
    expert_mode: bool = False
    timezone: str = "UTC"

    model_config = ConfigDict(populate_by_name=True)
