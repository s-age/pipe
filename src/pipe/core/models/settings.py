from pipe.core.models.base import CamelCaseModel
from pydantic import ConfigDict, Field


class HyperparameterValue(CamelCaseModel):
    """Represents the value and description of a hyperparameter."""

    value: float
    description: str


class Parameters(CamelCaseModel):
    """Container for model hyperparameters."""

    temperature: HyperparameterValue
    top_p: HyperparameterValue = Field(..., alias="top_p")
    top_k: HyperparameterValue = Field(..., alias="top_k")


class Settings(CamelCaseModel):
    """Represents the application settings loaded from setting.yml."""

    model: str = "gemini-2.5-flash"
    search_model: str = "gemini-2.5-flash"
    context_limit: int = 1000000
    api_mode: str = "gemini-api"
    language: str = "English"
    yolo: bool = False
    max_tool_calls: int = 10
    parameters: Parameters
    expert_mode: bool = False
    sessions_path: str = "sessions"
    reference_ttl: int = 3
    tool_response_expiration: int = 3
    timezone: str = "UTC"

    def to_api_dict(self) -> dict:
        """Convert settings to API-friendly dictionary format.

        Converts internal 'parameters' structure to public 'hyperparameters' format.

        Returns:
            Dictionary with hyperparameters instead of parameters
        """
        settings_dict = self.model_dump(by_alias=True)

        # Convert internal `parameters` to public `hyperparameters` mapping
        params = settings_dict.pop("parameters", None)
        hyperparameters: dict[str, float | None] = {}

        if params and isinstance(params, dict):
            hyperparameters = {
                "temperature": (
                    params.get("temperature", {}).get("value")
                    if isinstance(params.get("temperature"), dict)
                    else None
                ),
                "top_p": (
                    params.get("top_p", {}).get("value")
                    if isinstance(params.get("top_p"), dict)
                    else None
                ),
                "top_k": (
                    params.get("top_k", {}).get("value")
                    if isinstance(params.get("top_k"), dict)
                    else None
                ),
            }
        else:
            hyperparameters = {"temperature": None, "top_p": None, "top_k": None}

        settings_dict["hyperparameters"] = hyperparameters
        return settings_dict
