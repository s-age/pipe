"""Tests for the DeleteSessionRequest model."""

import pytest
from pipe.web.requests.sessions.delete_session import DeleteSessionRequest
from pydantic import ValidationError


class TestDeleteSessionRequest:
    """Tests for the DeleteSessionRequest model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        request = DeleteSessionRequest(session_id="test-session-123")
        assert request.session_id == "test-session-123"

    def test_initialization_with_camel_case(self):
        """Test that the request can be initialized using camelCase field names (via normalization)."""
        # BaseRequest.normalize_and_merge handles camelCase to snake_case conversion
        data = {"sessionId": "test-session-456"}
        request = DeleteSessionRequest.model_validate(data)
        assert request.session_id == "test-session-456"

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        request = DeleteSessionRequest(session_id="test-session-789")
        dumped = request.model_dump()
        assert "session_id" in dumped
        assert dumped["session_id"] == "test-session-789"

    def test_missing_session_id_raises_validation_error(self):
        """Test that missing session_id raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DeleteSessionRequest.model_validate({})

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("session_id",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)

    def test_create_with_path_params(self):
        """Test creating request with path parameters."""
        path_params = {"session_id": "path-session-123"}
        request = DeleteSessionRequest.create_with_path_params(
            path_params=path_params, body_data={}
        )
        assert request.session_id == "path-session-123"

    def test_create_with_path_params_and_body(self):
        """Test that body data can override path params if they share the same name."""
        path_params = {"session_id": "path-id"}
        body_data = {"session_id": "body-id"}
        request = DeleteSessionRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )
        assert request.session_id == "body-id"

    def test_forbid_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            DeleteSessionRequest.model_validate(
                {"session_id": "test", "extra_field": "not_allowed"}
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
