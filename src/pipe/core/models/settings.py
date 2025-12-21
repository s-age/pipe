from typing import Self

from pipe.core.models.base import CamelCaseModel
from pydantic import Field, model_validator


class HyperparameterValue(CamelCaseModel):
    """Represents the value and description of a hyperparameter."""

    value: float
    description: str


class Parameters(CamelCaseModel):
    """Container for model hyperparameters."""

    temperature: HyperparameterValue
    top_p: HyperparameterValue = Field(..., alias="top_p")
    top_k: HyperparameterValue = Field(..., alias="top_k")


class ModelConfig(CamelCaseModel):
    """Configuration for a specific model."""

    name: str
    context_limit: int
    cache_update_threshold: int


class Settings(CamelCaseModel):
    """Represents the application settings loaded from setting.yml."""

    model_config = {"protected_namespaces": ()}

    model_configs: list[ModelConfig] | None = None
    model: ModelConfig | str
    search_model: ModelConfig | str
    # Legacy fields for backward compatibility
    context_limit: int | None = None
    cache_update_threshold: int | None = None
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
    enable_sandbox: bool = True

    @model_validator(mode="after")
    def resolve_model_configs(self) -> Self:
        """Resolve model and search_model names to ModelConfig objects.

        Supports both new format (model_configs array) and legacy format
        (context_limit, cache_update_threshold as top-level fields).
        """
        # Legacy format support: create model_configs from top-level fields
        if self.model_configs is None:
            if self.context_limit is None:
                raise ValueError(
                    "Either 'model_configs' or 'context_limit' must be "
                    "provided in settings"
                )

            # Create default model configs from legacy fields
            model_name = (
                self.model if isinstance(self.model, str) else "gemini-2.5-flash"
            )
            search_model_name = (
                self.search_model if isinstance(self.search_model, str) else model_name
            )

            default_config = ModelConfig(
                name=model_name,
                context_limit=self.context_limit,
                cache_update_threshold=self.cache_update_threshold or 20000,
            )

            self.model_configs = [default_config]

            # Add search model config if different
            if search_model_name != model_name:
                search_config = ModelConfig(
                    name=search_model_name,
                    context_limit=self.context_limit,
                    cache_update_threshold=self.cache_update_threshold or 20000,
                )
                self.model_configs.append(search_config)

        # Resolve main model
        if isinstance(self.model, str):
            model_name = self.model
            model_config = self._find_model_config(model_name)
            if not model_config:
                raise ValueError(
                    f"Model '{model_name}' not found in model_configs. "
                    f"Available models: {[m.name for m in self.model_configs]}"
                )
            self.model = model_config

        # Resolve search model
        if isinstance(self.search_model, str):
            search_model_name = self.search_model
            search_model_config = self._find_model_config(search_model_name)
            if not search_model_config:
                raise ValueError(
                    f"Search model '{search_model_name}' not found in model_configs. "
                    f"Available models: {[m.name for m in self.model_configs]}"
                )
            self.search_model = search_model_config

        return self

    def _find_model_config(self, model_name: str) -> ModelConfig | None:
        """Find a model config by name."""
        if self.model_configs is None:
            return None
        for config in self.model_configs:
            if config.name == model_name:
                return config
        return None

    def to_api_dict(self) -> dict:
        """Convert settings to API-friendly dictionary format.

        Converts internal 'parameters' structure to public 'hyperparameters' format.
        Flattens model config for backward compatibility with Web API consumers.

        Returns:
            Dictionary with hyperparameters instead of parameters
        """
        settings_dict = self.model_dump(by_alias=True)

        # Remove model_configs array from API output
        settings_dict.pop("modelConfigs", None)
        settings_dict.pop("model_configs", None)

        # Flatten model config to top-level for backward compatibility
        if isinstance(self.model, ModelConfig):
            settings_dict["model"] = self.model.name
            settings_dict["contextLimit"] = self.model.context_limit
            settings_dict["cacheUpdateThreshold"] = self.model.cache_update_threshold

        # Flatten search_model config
        if isinstance(self.search_model, ModelConfig):
            settings_dict["searchModel"] = self.search_model.name

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
