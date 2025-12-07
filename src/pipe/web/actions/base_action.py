"""Base Action class for all API actions."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from flask import Request
from pipe.web.request_context import RequestContext
from pipe.web.requests.base_request import BaseRequest
from pydantic import BaseModel

TBody = TypeVar("TBody", bound=BaseModel)
TRequest = TypeVar("TRequest", bound=BaseRequest)


class BaseAction(ABC, Generic[TBody, TRequest]):
    """Abstract base class for all API actions.

    Type parameters:
        TBody: Pydantic model type for request body (legacy pattern)
        TRequest: BaseRequest subclass type (new pattern)

    Two patterns are supported:

    1. Legacy pattern (body_model): For backward compatibility
       - Set body_model class variable to specify request body Pydantic model
       - Access via self.request.get_body()
       - Validation happens lazily when get_body() is called

    2. New pattern (request_model): Laravel/Struts style
       - Set request_model class variable to a BaseRequest subclass
       - Validation happens BEFORE action execution in dispatcher
       - Access validated request via self.validated_request
       - Path params and body are unified and validated together
       - Full type safety with IDE completion

    Examples:
        # New pattern with type safety
        class CreateSessionAction(BaseAction[Any, CreateSessionRequest]):
            request_model = CreateSessionRequest

            def execute(self):
                req = self.validated_request  # Type: CreateSessionRequest
                return service.create(req.session_id)  # IDE completion works!

        # Legacy pattern (still supported)
        class UpdateSessionAction(BaseAction[UpdateSessionBody, Any]):
            body_model = UpdateSessionBody

            def execute(self):
                body = self.request.get_body()  # Type: UpdateSessionBody
                return service.update(body.name)
    """

    # Legacy: Pydantic model for request body only
    body_model: type[TBody] | None = None

    # New: BaseRequest subclass for unified path params + body validation
    request_model: type[TRequest] | None = None

    def __init__(
        self,
        params: dict | None = None,
        request_data: Request | None = None,
        request_context: RequestContext[TBody] | None = None,
        validated_request: TRequest | None = None,
    ):
        """Initialize the action with parameters and optional request data.

        Args:
            params: (Legacy) Parameters extracted from the URL path and query string
            request_data: (Legacy) Optional Flask Request object for accessing request
                body
            request_context: RequestContext object providing unified access to validated
                parameters
            validated_request: Pre-validated BaseRequest instance (if using
                request_model pattern)
        """
        # Support legacy initialization
        if request_context is None:
            request_context = RequestContext(
                path_params=params or {},
                request_data=request_data,
                body_model=self.body_model,
            )

        self.request = request_context
        self.validated_request = validated_request

        # Keep legacy attributes for backward compatibility
        self.params = params or {}
        self.request_data = request_data

    @abstractmethod
    def execute(self) -> Any:
        """Execute the action and return the result.

        Actions should return the business logic result directly.
        The dispatcher will wrap it in ApiResponse and handle errors.

        Return types:
        - Data object: Wrapped in ApiResponse with 200 status
        - tuple[dict, int]: Legacy support for (response_dict, status_code)
        - tuple[ApiResponse, int]: Legacy support
        - Response: Flask Response object (for streaming, etc.)

        Error handling:
        - Raise HttpException subclasses for specific HTTP errors
        - Raise any Exception for 500 Internal Server Error
        - No need to catch and format errors yourself

        Returns:
            Business logic result (any type)

        Raises:
            HttpException: For specific HTTP status codes
            Exception: For unexpected errors (becomes 500)

        Examples:
            # New pattern - return data directly
            def execute(self):
                req = self.validated_request
                result = service.do_something(req.param)
                return result  # Dispatcher wraps in ApiResponse

            # Raise errors for non-200 responses
            def execute(self):
                if not found:
                    raise NotFoundError("Resource not found")
                return data
        """
        pass
