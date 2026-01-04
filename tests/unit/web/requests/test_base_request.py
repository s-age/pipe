"""Unit tests for the BaseRequest class."""

from typing import ClassVar

import pytest
from pipe.web.requests.base_request import BaseRequest
from pydantic import ValidationError


class MockRequest(BaseRequest):
    """Concrete subclass of BaseRequest for testing."""

    path_params: ClassVar[list[str]] = ["session_id"]

    session_id: str
    name: str | None = None
    age: int | None = None


class TestBaseRequest:
    """Tests for the BaseRequest class."""

    def test_normalize_and_merge_camel_case(self):
        """Test that camelCase keys are normalized to snake_case."""
        data = {"sessionId": "test-123", "name": "John Doe", "age": 30}
        # BaseRequest.normalize_and_merge is a model_validator(mode="before")
        # It's called during initialization.
        request = MockRequest.model_validate(data)
        assert request.session_id == "test-123"
        assert request.name == "John Doe"
        assert request.age == 30

    def test_create_with_path_params(self):
        """Test creating a request with path parameters and body data."""
        path_params = {"session_id": "path-session-123"}
        body_data = {"name": "Body Name", "age": 25}

        request = MockRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )

        assert isinstance(request, MockRequest)
        assert request.session_id == "path-session-123"
        assert request.name == "Body Name"
        assert request.age == 25

    def test_create_with_path_params_override(self):
        """Test that body data can override path parameters if they share keys."""
        path_params = {"session_id": "path-session"}
        body_data = {"session_id": "body-session", "name": "Test"}

        request = MockRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )

        assert request.session_id == "body-session"
        assert request.name == "Test"

    def test_create_with_path_params_missing_in_dict(self):
        """Test behavior when a declared path param is missing from the input dict."""
        path_params: dict[str, str | int | bool] = {}  # session_id is missing
        body_data = {"name": "Test"}

        # This should raise ValidationError because session_id is required in MockRequest
        with pytest.raises(ValidationError) as exc_info:
            MockRequest.create_with_path_params(
                path_params=path_params, body_data=body_data
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("session_id",) and error["type"] == "missing"
            for error in errors
        )

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden by model_config."""
        with pytest.raises(ValidationError) as exc_info:
            MockRequest(session_id="test", extra_field="not allowed")

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)

    def test_validate_assignment(self):
        """Test that validation occurs on assignment."""
        request = MockRequest(session_id="test", age=20)

        with pytest.raises(ValidationError) as exc_info:
            request.age = "not an int"  # type: ignore

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("age",) for error in errors)

    def test_normalize_and_merge_nested(self):
        """Test normalization of nested camelCase keys."""

        # For this we need a model with nested structure
        class NestedModel(BaseRequest):
            user_info: dict

        data = {"userInfo": {"firstName": "John", "lastName": "Doe"}}
        request = NestedModel.model_validate(data)
        # normalize_camel_case_keys is recursive
        dumped = request.model_dump()
        assert "user_info" in dumped
        assert dumped["user_info"]["first_name"] == "John"
        assert dumped["user_info"]["last_name"] == "Doe"

    def test_create_with_path_params_no_body(self):
        """Test create_with_path_params with None body_data."""
        path_params = {"session_id": "only-path"}
        request = MockRequest.create_with_path_params(path_params=path_params)
        assert request.session_id == "only-path"
        assert request.name is None
