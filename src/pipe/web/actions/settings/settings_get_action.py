"""Settings get action."""

from typing import TypedDict

from pipe.web.actions.base_action import BaseAction
from pipe.web.service_container import get_settings


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
        settings = get_settings()
        return {"settings": settings.to_api_dict()}  # type: ignore[typeddict-item]
