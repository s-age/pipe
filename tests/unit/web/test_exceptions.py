"""Unit tests for custom HTTP exceptions."""

from pipe.web.exceptions import (
    BadRequestError,
    HttpException,
    InternalServerError,
    NotFoundError,
    UnprocessableEntityError,
)


class TestHttpException:
    """Tests for the base HttpException class."""

    def test_initialization(self):
        """Test that HttpException initializes with correct message and status code."""
        message = "Internal error"
        exc = HttpException(message)
        assert exc.message == message
        assert exc.status_code == 500
        assert str(exc) == message

    def test_custom_status_code_subclass(self):
        """Test that a subclass can override the default status code."""

        class CustomError(HttpException):
            status_code = 418

        exc = CustomError("I'm a teapot")
        assert exc.status_code == 418


class TestBadRequestError:
    """Tests for BadRequestError."""

    def test_status_code(self):
        """Test that BadRequestError has status code 400."""
        exc = BadRequestError("Bad request")
        assert exc.status_code == 400
        assert exc.message == "Bad request"


class TestNotFoundError:
    """Tests for NotFoundError."""

    def test_status_code(self):
        """Test that NotFoundError has status code 404."""
        exc = NotFoundError("Not found")
        assert exc.status_code == 404
        assert exc.message == "Not found"


class TestUnprocessableEntityError:
    """Tests for UnprocessableEntityError."""

    def test_status_code(self):
        """Test that UnprocessableEntityError has status code 422."""
        exc = UnprocessableEntityError("Unprocessable entity")
        assert exc.status_code == 422
        assert exc.message == "Unprocessable entity"


class TestInternalServerError:
    """Tests for InternalServerError."""

    def test_status_code(self):
        """Test that InternalServerError has status code 500."""
        exc = InternalServerError("Internal server error")
        assert exc.status_code == 500
        assert exc.message == "Internal server error"
