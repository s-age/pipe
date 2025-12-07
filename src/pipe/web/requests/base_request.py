"""Base request class for all API request models."""

from typing import Any, ClassVar

from pipe.web.requests.common import normalize_camel_case_keys
from pydantic import BaseModel, ConfigDict, model_validator


class BaseRequest(BaseModel):
    """Base class for all API request models.

    This class provides:
    1. Automatic camelCase to snake_case conversion
    2. Path parameters integration (can be injected by subclasses)
    3. Validation for both path parameters and request body

    Subclasses should define:
    - Body fields as regular Pydantic fields
    - path_params: ClassVar[list[str]] to declare which path params are expected

    Example:
        class SessionEditRequest(BaseRequest):
            path_params: ClassVar[list[str]] = ["session_id"]

            # Path parameter (injected from URL)
            session_id: str

            # Body fields
            purpose: str | None = None
            background: str | None = None
    """

    model_config = ConfigDict(
        # Allow extra fields for backward compatibility
        extra="forbid",
        # Validate on assignment
        validate_assignment=True,
    )

    # Subclasses can declare which path parameters they expect
    path_params: ClassVar[list[str]] = []

    @model_validator(mode="before")
    @classmethod
    def normalize_and_merge(cls, data: Any) -> Any:
        """Normalize camelCase keys to snake_case.

        This validator is called before field validation, allowing frontend
        to send camelCase while backend uses snake_case consistently.
        """
        return normalize_camel_case_keys(data)

    @classmethod
    def create_with_path_params(
        cls,
        path_params: dict[str, Any],
        body_data: dict[str, Any] | None = None,
    ) -> "BaseRequest":
        """Create a request instance with path parameters and body data.

        This method is used by the dispatcher to merge path parameters
        with request body before validation.

        Args:
            path_params: Path parameters extracted from URL
            body_data: Request body data (already converted from camelCase)

        Returns:
            Validated request instance

        Raises:
            ValidationError: If validation fails
        """
        # Merge path params with body data
        merged_data = {}

        # Add path parameters
        for param_name in cls.path_params:
            if param_name in path_params:
                merged_data[param_name] = path_params[param_name]

        # Add body data
        if body_data:
            merged_data.update(body_data)

        # Create and validate
        return cls(**merged_data)
