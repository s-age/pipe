from typing import Any

from pipe.web.actions.base_action import BaseAction


class SettingsGetAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import settings

        try:
            settings_dict: dict[str, Any] = settings.model_dump()

            # Convert internal `parameters` structure to the public `hyperparameters` mapping
            params = settings_dict.pop("parameters", None)
            if params and isinstance(params, dict):
                hp: dict[str, Any] = {}
                for key in ("temperature", "top_p", "top_k"):
                    val = params.get(key)
                    if isinstance(val, dict) and "value" in val:
                        hp[key] = val["value"]
                    else:
                        hp[key] = None

                settings_dict["hyperparameters"] = hp

            return {"settings": settings_dict}, 200
        except Exception as e:
            return {"message": str(e)}, 500
