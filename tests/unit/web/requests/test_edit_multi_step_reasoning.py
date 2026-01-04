"""Unit tests for EditMultiStepReasoningRequest."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.edit_multi_step_reasoning import (
    EditMultiStepReasoningRequest,
)
from pydantic import ValidationError


class TestEditMultiStepReasoningRequest:
    """Tests for the EditMultiStepReasoningRequest model."""

    @pytest.fixture
    def mock_session_service(self):
        """Mock the session service."""
        with patch("pipe.web.service_container.get_session_service") as mock_get:
            mock_service = MagicMock()
            mock_get.return_value = mock_service
            yield mock_service

    def test_initialization_success(self, mock_session_service):
        """Test successful initialization with valid data."""
        mock_session_service.get_session.return_value = {
            "session_id": "test-session-123"
        }

        request = EditMultiStepReasoningRequest(
            session_id="test-session-123", multi_step_reasoning_enabled=True
        )

        assert request.session_id == "test-session-123"
        assert request.multi_step_reasoning_enabled is True
        mock_session_service.get_session.assert_called_once_with("test-session-123")

    def test_initialization_with_camel_case(self, mock_session_service):
        """Test initialization with camelCase keys (normalization)."""
        mock_session_service.get_session.return_value = {
            "session_id": "test-session-123"
        }

        # Pydantic will call normalize_keys before validation
        data = {
            "sessionId": "test-session-123",
            "multiStepReasoningEnabled": True,
        }
        request = EditMultiStepReasoningRequest.model_validate(data)

        assert request.session_id == "test-session-123"
        assert request.multi_step_reasoning_enabled is True

    def test_missing_session_id(self):
        """Test validation error when session_id is missing."""
        with pytest.raises(ValidationError) as exc_info:
            EditMultiStepReasoningRequest(multi_step_reasoning_enabled=True)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("session_id",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)

    def test_missing_multi_step_reasoning_enabled(self):
        """Test validation error when multi_step_reasoning_enabled is missing."""
        with pytest.raises(ValidationError) as exc_info:
            EditMultiStepReasoningRequest(session_id="test-session-123")

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("multi_step_reasoning_enabled",) for error in errors
        )
        assert any(error["type"] == "missing" for error in errors)

    def test_session_not_found(self, mock_session_service):
        """Test that NotFoundError is raised when session does not exist."""
        mock_session_service.get_session.return_value = None

        with pytest.raises(NotFoundError, match="Session not found."):
            EditMultiStepReasoningRequest(
                session_id="non-existent", multi_step_reasoning_enabled=True
            )

    def test_create_with_path_params(self, mock_session_service):
        """Test create_with_path_params method."""
        mock_session_service.get_session.return_value = {
            "session_id": "test-session-123"
        }

        path_params = {"session_id": "test-session-123"}
        body_data = {"multi_step_reasoning_enabled": False}

        request = EditMultiStepReasoningRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )

        assert request.session_id == "test-session-123"
        assert request.multi_step_reasoning_enabled is False

    def test_extra_fields_forbidden(self, mock_session_service):
        """Test that extra fields are forbidden."""
        mock_session_service.get_session.return_value = {
            "session_id": "test-session-123"
        }

        with pytest.raises(ValidationError) as exc_info:
            EditMultiStepReasoningRequest(
                session_id="test-session-123",
                multi_step_reasoning_enabled=True,
                extra_field="not-allowed",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
