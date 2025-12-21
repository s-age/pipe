"""
Streaming Dispatcher for handling actions that return streaming responses.

This dispatcher handles actions that return Flask Response objects
with streaming content, such as Server-Sent Events (SSE).
Unlike the regular dispatcher, this does not wrap results
in ApiResponse and handles streaming responses directly.
"""

from flask import Response
from pipe.web.actions.base_action import BaseAction
from pipe.web.binder import RequestBinder
from pipe.web.dispatcher import get_dispatcher
from pipe.web.exceptions import HttpException
from pipe.web.request_context import RequestContext
from pydantic import ValidationError


def dispatch_streaming_action(
    action_class: type[BaseAction],
    params: dict[str, str],
    request_data: RequestContext,
) -> Response:
    """
    Dispatch a streaming action that returns a Flask Response.

    Args:
        action_class: The action class to instantiate and execute
        params: Path parameters from the route
        request_data: Request context containing body and path params

    Returns:
        Flask Response object with streaming content

    Raises:
        HttpException: For HTTP-specific errors (400, 404, 422, 500)
        Exception: For unexpected errors
    """
    # Extract the Flask request
    flask_request = None
    if hasattr(request_data, "_request_data") and request_data._request_data:
        flask_request = request_data._request_data

    # Use the dispatcher's binder and factory for consistency
    dispatcher = get_dispatcher()
    binder = RequestBinder()

    # 1. Bind & Validate Request
    try:
        validated_data = binder.bind(action_class, flask_request, params)
    except ValidationError as e:
        from pipe.web.exceptions import UnprocessableEntityError

        error_messages = [
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
            for err in e.errors()
        ]
        raise UnprocessableEntityError("; ".join(error_messages))
    except Exception as e:
        if isinstance(e, HttpException):
            raise
        from pipe.web.exceptions import InternalServerError

        raise InternalServerError(str(e))

    # 2. Prepare Runtime Context
    runtime_context = {
        "params": params,
        "request_data": flask_request,
        "request_context": request_data,
        "validated_request": validated_data,
    }

    # 3. Instantiate Action using GenericActionFactory (with DI)
    try:
        action = dispatcher.factory.create(action_class, runtime_context)

        # Manual injection fallback for request_context (specific to streaming)
        if hasattr(action, "request_context") and not getattr(
            action, "request_context", None
        ):
            action.request_context = request_data  # type: ignore

    except Exception as e:
        from pipe.web.exceptions import InternalServerError

        raise InternalServerError(f"Failed to create action: {str(e)}")

    # 4. Execute the action - should return Flask Response
    try:
        result = action.execute()

        # Verify result is a Response object
        if not isinstance(result, Response):
            raise TypeError(
                f"Streaming action {action_class.__name__} must return Flask Response, "
                f"got {type(result).__name__}"
            )

        return result

    except HttpException:
        # Re-raise HTTP exceptions to be handled by error handler
        raise
    except Exception as e:
        # Wrap unexpected exceptions
        from pipe.web.exceptions import InternalServerError

        raise InternalServerError(str(e))
