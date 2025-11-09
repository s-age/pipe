from typing import Any

from pipe.web.actions.base_action import BaseAction


class SettingsGetAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import settings

        try:
            return {"settings": settings.model_dump()}, 200
        except Exception as e:
            return {"message": str(e)}, 500
