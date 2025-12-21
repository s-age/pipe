import re
from typing import Any

from flask import Request
from pipe.web.requests.base_request import BaseRequest


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def _convert_keys_to_snake(data: dict | list | Any) -> dict | list | Any:
    """Recursively convert all dict keys from camelCase to snake_case."""
    if isinstance(data, dict):
        return {_camel_to_snake(k): _convert_keys_to_snake(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_keys_to_snake(item) for item in data]
    else:
        return data


def _convert_keys_to_camel(data: dict | list | Any) -> dict | list | Any:
    """Recursively convert all dict keys from snake_case to camelCase."""
    if isinstance(data, dict):
        return {_snake_to_camel(k): _convert_keys_to_camel(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_keys_to_camel(item) for item in data]
    else:
        return data


class RequestBinder:
    """Binds HTTP request data to the Action's expected format."""

    def bind(self, action_class: type, raw_request: Request, route_params: dict) -> Any:
        """
        Parses request, converts keys, and validates against action.request_model.
        Returns the validated object (if request_model exists) or the converted
        dictionary.
        Throws ValidationError (from pydantic) on failure.
        """
        # 1. Data Normalization (Camel -> Snake)
        converted_json = None
        if raw_request.is_json:
            original_json = raw_request.get_json(silent=True)
            if original_json:
                converted_json = _convert_keys_to_snake(original_json)

        # 2. Validation
        request_model = getattr(action_class, "request_model", None)

        if request_model and issubclass(request_model, BaseRequest):
            # Pydantic Validation (Fail Fast)
            return request_model.create_with_path_params(
                path_params=route_params, body_data=converted_json
            )

        return converted_json
