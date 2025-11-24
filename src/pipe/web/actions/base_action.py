"""Base Action class for all API actions."""

from abc import ABC, abstractmethod
from typing import Any

from flask import Request


class BaseAction(ABC):
    """Abstract base class for all API actions."""

    def __init__(self, params: dict, request_data: Request | None = None):
        """Initialize the action with parameters and optional request data.

        Args:
            params: Parameters extracted from the URL path and query string
            request_data: Optional Flask Request object for accessing request body
        """
        self.params = params
        self.request_data = request_data

    @abstractmethod
    def execute(self) -> tuple[dict[str, Any], int]:
        """Execute the action and return a JSON response with status code.

        Returns:
            A tuple of (response_dict, status_code)
        """
        pass
