"""Settings get action."""

from pipe.web.action_responses import SettingsResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.service_container import get_settings


class SettingsGetAction(BaseAction):
    def execute(self) -> SettingsResponse:
        settings = get_settings()
        return SettingsResponse(settings=settings.to_api_dict())
