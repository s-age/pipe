"""
Unit tests for the EditSessionMetaRequest model.
"""

import pytest
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.web.requests.sessions.edit_session_meta import EditSessionMetaRequest
from pydantic import ValidationError


class TestEditSessionMetaRequest:
    """Tests for the EditSessionMetaRequest model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        request = EditSessionMetaRequest(
            session_id="test-session-123",
            purpose="Test purpose",
            background="Test background",
            roles=["role1"],
            artifacts=["art1"],
            procedure="proc1",
            multi_step_reasoning_enabled=True,
            token_count=1000,
            hyperparameters=Hyperparameters(temperature=0.7),
        )
        assert request.session_id == "test-session-123"
        assert request.purpose == "Test purpose"
        assert request.background == "Test background"
        assert request.roles == ["role1"]
        assert request.artifacts == ["art1"]
        assert request.procedure == "proc1"
        assert request.multi_step_reasoning_enabled is True
        assert request.token_count == 1000
        assert request.hyperparameters.temperature == 0.7

    def test_initialization_with_camel_case(self):
        """Test that the request can be initialized using camelCase field names (normalization)."""
        data = {
            "sessionId": "test-session-123",
            "multiStepReasoningEnabled": True,
            "tokenCount": 500,
        }
        request = EditSessionMetaRequest.model_validate(data)
        assert request.session_id == "test-session-123"
        assert request.multi_step_reasoning_enabled is True
        assert request.token_count == 500

    def test_validation_at_least_one_field_success(self):
        """Test that validation passes when at least one body field is provided."""
        # Only purpose
        request = EditSessionMetaRequest(session_id="test", purpose="something")
        assert request.purpose == "something"

        # Only hyperparameters
        request = EditSessionMetaRequest(
            session_id="test", hyperparameters=Hyperparameters(top_p=0.9)
        )
        assert request.hyperparameters.top_p == 0.9

    def test_validation_at_least_one_field_failure(self):
        """Test that validation fails when no body fields are provided."""
        with pytest.raises(ValidationError) as exc_info:
            EditSessionMetaRequest(session_id="test-session-123")

        assert "At least one of" in str(exc_info.value)
        assert "must be present" in str(exc_info.value)

    def test_hyperparameters_nested_validation(self):
        """Test that nested hyperparameters are validated."""
        # Invalid temperature (ge=0.0, le=2.0)
        with pytest.raises(ValidationError):
            EditSessionMetaRequest(
                session_id="test",
                hyperparameters={"temperature": 2.5},
            )

    def test_create_with_path_params(self):
        """Test creating request with path parameters and body data."""
        path_params = {"session_id": "path-session-123"}
        body_data = {"purpose": "Updated purpose"}

        request = EditSessionMetaRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )

        assert request.session_id == "path-session-123"
        assert request.purpose == "Updated purpose"

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            EditSessionMetaRequest(
                session_id="test",
                purpose="test",
                unknown_field="not allowed",
            )

        assert "extra_forbidden" in str(exc_info.value)

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        request = EditSessionMetaRequest(
            session_id="test-session-789",
            purpose="Serialization test",
        )
        dumped = request.model_dump()
        assert dumped["session_id"] == "test-session-789"
        assert dumped["purpose"] == "Serialization test"
        assert dumped["background"] is None
