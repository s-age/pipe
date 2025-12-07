from typing import TypedDict

from pipe.web.actions.base_action import BaseAction


class HyperparameterDict(TypedDict):
    """Hyperparameter values exposed to API."""

    temperature: float | None
    top_p: float | None
    top_k: float | None


class SettingsDict(TypedDict, total=False):
    """Settings data structure matching Settings model."""

    model: str
    search_model: str
    context_limit: int
    api_mode: str
    language: str
    yolo: bool
    max_tool_calls: int
    expert_mode: bool
    sessions_path: str
    reference_ttl: int
    tool_response_expiration: int
    timezone: str
    hyperparameters: HyperparameterDict


class SettingsResponse(TypedDict):
    """Response containing settings data."""

    settings: SettingsDict


class SettingsGetAction(BaseAction):
    def execute(self) -> SettingsResponse:
        from pipe.web.service_container import get_settings

        settings_dict = get_settings().model_dump()

        # Convert internal `parameters` to public `hyperparameters` mapping
        params = settings_dict.pop("parameters", None)
        hp: HyperparameterDict
        if params and isinstance(params, dict):
            hp = {
                "temperature": params.get("temperature", {}).get("value")
                if isinstance(params.get("temperature"), dict)
                else None,
                "top_p": params.get("top_p", {}).get("value")
                if isinstance(params.get("top_p"), dict)
                else None,
                "top_k": params.get("top_k", {}).get("value")
                if isinstance(params.get("top_k"), dict)
                else None,
            }
        else:
            hp = {"temperature": None, "top_p": None, "top_k": None}

        settings_dict["hyperparameters"] = hp

        return {"settings": settings_dict}  # type: ignore[typeddict-item]
