"""
Streaming Dispatcher for handling actions that return streaming responses.

This dispatcher handles actions that return Flask Response objects
with streaming content, such as Server-Sent Events (SSE).
Unlike the regular dispatcher, this does not wrap results
in ApiResponse and handles streaming responses directly.
"""

from flask import Response
from pipe.web.actions.base_action import BaseAction
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

    # Pre-validate with request_model if present (new pattern)
    if hasattr(action_class, "request_model") and action_class.request_model:
        try:
            # Extract body from the underlying Flask request
            body_data = None
            flask_request = None
            if hasattr(request_data, "_request_data") and request_data._request_data:
                flask_request = request_data._request_data
                if flask_request.is_json:
                    body_data = flask_request.get_json(silent=True)

            validated = action_class.request_model.create_with_path_params(
                path_params=params, body_data=body_data
            )

            # Create action WITH validated_request and request_context
            action = action_class(
                params=params,
                request_data=flask_request,
                request_context=request_data,
                validated_request=validated,
            )
        except ValidationError as e:
            from pipe.web.exceptions import UnprocessableEntityError

            raise UnprocessableEntityError(str(e))
    # Also support body_model for legacy actions
    elif hasattr(action_class, "body_model") and action_class.body_model:
        try:
            # Extract body from the underlying Flask request
            body_data = None
            flask_request = None
            if hasattr(request_data, "_request_data") and request_data._request_data:
                flask_request = request_data._request_data
                if flask_request.is_json:
                    body_data = flask_request.get_json(silent=True)

            validated = (
                action_class.body_model(**body_data)
                if body_data
                else action_class.body_model()
            )

            # Create action WITH validated body and request_context
            action = action_class(
                params=params,
                request_data=flask_request,
                request_context=request_data,
                validated_request=validated,
            )
        except ValidationError as e:
            from pipe.web.exceptions import UnprocessableEntityError

            raise UnprocessableEntityError(str(e))
    else:
        # No validation model - create action normally
        flask_request = None
        if hasattr(request_data, "_request_data") and request_data._request_data:
            flask_request = request_data._request_data
        action = action_class(
            params=params, request_data=flask_request, request_context=request_data
        )

    # Execute the action - should return Flask Response
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
