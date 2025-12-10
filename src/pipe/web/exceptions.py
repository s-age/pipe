"""Custom exceptions for HTTP error handling.

These exceptions allow actions to raise specific HTTP errors
without handling response formatting themselves.
"""


class HttpException(Exception):
    """Base exception for HTTP errors.

    Actions can raise these to indicate specific HTTP status codes.
    The dispatcher will catch these and format appropriate responses.

    Attributes:
        status_code: HTTP status code
        message: Error message
    """

    status_code: int = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BadRequestError(HttpException):
    """400 Bad Request - Invalid input data."""

    status_code = 400


class NotFoundError(HttpException):
    """404 Not Found - Resource doesn't exist."""

    status_code = 404


class UnprocessableEntityError(HttpException):
    """422 Unprocessable Entity - Validation error."""

    status_code = 422


class InternalServerError(HttpException):
    """500 Internal Server Error - Unexpected error."""

    status_code = 500
