"""
Pydantic model for validating the request body of the edit hyperparameters API endpoint.

Behaviour:
- Accepts any subset of fields (temperature, top_p, top_k) but disallows null
  values for any provided field.
- Accepts camelCase keys (topP, topK) and normalizes them to snake_case.
- Validates numeric types and ranges:
  - temperature: float >= 0.0
  - top_p: float in [0.0, 1.0]
  - top_k: int >= 0
"""

from typing import ClassVar

from pipe.web.requests.base_request import BaseRequest
from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import model_validator


class EditHyperparametersRequest(BaseRequest):
    path_params: ClassVar[list[str]] = ["session_id"]

    # Path parameter (from URL)
    session_id: str

    # Body fields (all optional, at least one required)
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_and_validate(cls, data: dict | list) -> dict:
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object.")

        # Normalize camelCase to snake_case
        normalized = normalize_camel_case_keys(data)
        assert isinstance(normalized, dict)  # Type narrowing for mypy
        data = normalized

        # Require at least one hyperparameter field
        if not any(k in data for k in ("temperature", "top_p", "top_k")):
            raise ValueError(
                "At least one of ['temperature', 'top_p', 'top_k'] must be provided."
            )

        # temperature
        if "temperature" in data:
            if data["temperature"] is None:
                raise ValueError("'temperature' cannot be null.")
            try:
                t = float(data["temperature"])  # type: ignore[arg-type]
            except Exception:
                raise ValueError("'temperature' must be a number.")
            if t < 0.0:
                raise ValueError("'temperature' must be >= 0.")
            data["temperature"] = t

        # top_p
        if "top_p" in data:
            if data["top_p"] is None:
                raise ValueError("'top_p' cannot be null.")
            try:
                p = float(data["top_p"])  # type: ignore[arg-type]
            except Exception:
                raise ValueError("'top_p' must be a number between 0.0 and 1.0.")
            if not (0.0 <= p <= 1.0):
                raise ValueError("'top_p' must be between 0.0 and 1.0.")
            data["top_p"] = p

        # top_k
        if "top_k" in data:
            if data["top_k"] is None:
                raise ValueError("'top_k' cannot be null.")
            # Allow numeric strings/floats that represent integers, but coerce to int
            try:
                k_raw = data["top_k"]
                if isinstance(k_raw, float) and not k_raw.is_integer():
                    raise ValueError("'top_k' must be an integer.")
                k = int(k_raw)
            except Exception:
                raise ValueError("'top_k' must be an integer >= 0.")
            if k < 0:
                raise ValueError("'top_k' must be >= 0.")
            data["top_k"] = k

        return data
