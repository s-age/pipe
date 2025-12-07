"""RequestContext for unified access to request parameters and body."""

from typing import Any, Generic, TypeVar

from flask import Request
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class RequestContext(Generic[T]):
    """
    Unified request context that provides validated access
    to path params and body.
    """

    def __init__(
        self,
        path_params: dict[str, Any],
        request_data: Request | None = None,
        body_model: type[T] | None = None,
    ):
        """Initialize the request context.

        Args:
            path_params: Parameters extracted from URL path
                (already converted from camelCase)
            request_data: Flask Request object
                (body already converted from camelCase)
            body_model: Optional Pydantic model for request body validation
        """
        self._path_params = path_params
        self._request_data = request_data
        self._body_model = body_model
        self._validated_body: T | None = None
        self._body_errors: list[str] | None = None

    def get_path_param(self, key: str, required: bool = True) -> Any:
        """Get a path parameter with optional requirement validation.

        Args:
            key: The parameter name (snake_case)
            required: Whether the parameter is required

        Returns:
            The parameter value or None if not found and not required

        Raises:
            ValueError: If the parameter is required but not found
        """
        value = self._path_params.get(key)
        if value is None and required:
            raise ValueError(f"Required path parameter '{key}' is missing")
        return value

    def get_path_param_int(self, key: str, required: bool = True) -> int | None:
        """Get a path parameter as an integer.

        Args:
            key: The parameter name (snake_case)
            required: Whether the parameter is required

        Returns:
            The parameter value as an integer or None if not found and not required

        Raises:
            ValueError: If the parameter is required but not found
                or cannot be converted
        """
        value = self.get_path_param(key, required)
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Path parameter '{key}' must be an integer, got: {value}"
            ) from e

    def get_body(self) -> T:
        """Get the validated request body.

        Returns:
            The validated request body as a Pydantic model

        Raises:
            ValueError: If body validation fails or no body model is configured
        """
        if self._body_model is None:
            raise ValueError("No body model configured for this request")

        if self._validated_body is not None:
            return self._validated_body

        if self._body_errors is not None:
            raise ValueError("; ".join(self._body_errors))

        if not self._request_data or not self._request_data.is_json:
            self._body_errors = ["Request body must be JSON"]
            raise ValueError("; ".join(self._body_errors))

        body_data = self._request_data.get_json(silent=True)
        if body_data is None:
            self._body_errors = ["No request body provided"]
            raise ValueError("; ".join(self._body_errors))

        try:
            self._validated_body = self._body_model(**body_data)
            return self._validated_body
        except ValidationError as e:
            self._body_errors = [err["msg"] for err in e.errors()]
            raise ValueError("; ".join(self._body_errors)) from e

    def has_body(self) -> bool:
        """Check if the request has a JSON body.

        Returns:
            True if the request has a JSON body, False otherwise
        """
        return (
            self._request_data is not None
            and self._request_data.is_json
            and self._request_data.get_json(silent=True) is not None
        )

    @property
    def raw_request(self) -> Request | None:
        """Get the underlying Flask Request object for advanced use cases.

        Returns:
            The Flask Request object or None if not available
        """
        return self._request_data
