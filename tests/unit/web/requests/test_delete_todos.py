"""Unit tests for DeleteTodosRequest."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.delete_todos import DeleteTodosRequest
from pydantic import ValidationError


class TestDeleteTodosRequest:
    """Tests for the DeleteTodosRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    def test_initialization_success(self, mock_get_service):
        """Test successful initialization when session exists."""
        mock_service = MagicMock()
        mock_service.get_session.return_value = {"session_id": "test-session-123"}
        mock_get_service.return_value = mock_service

        request = DeleteTodosRequest(session_id="test-session-123")
        assert request.session_id == "test-session-123"
        mock_service.get_session.assert_called_once_with("test-session-123")

    @patch("pipe.web.service_container.get_session_service")
    def test_initialization_session_not_found(self, mock_get_service):
        """Test that NotFoundError is raised when session does not exist."""
        mock_service = MagicMock()
        mock_service.get_session.return_value = None
        mock_get_service.return_value = mock_service

        with pytest.raises(NotFoundError, match="Session not found."):
            DeleteTodosRequest(session_id="non-existent")

    def test_missing_session_id_raises_validation_error(self):
        """Test that missing session_id raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DeleteTodosRequest.model_validate({})

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("session_id",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service):
        """Test creating request with path parameters."""
        mock_service = MagicMock()
        mock_service.get_session.return_value = {"session_id": "path-session-123"}
        mock_get_service.return_value = mock_service

        request = DeleteTodosRequest.create_with_path_params(
            path_params={"session_id": "path-session-123"},
            body_data={},
        )
        assert request.session_id == "path-session-123"
        assert isinstance(request, DeleteTodosRequest)

    @patch("pipe.web.service_container.get_session_service")
    def test_serialization(self, mock_get_service):
        """Test that model_dump() returns the correct structure."""
        mock_service = MagicMock()
        mock_service.get_session.return_value = {"session_id": "test-session-789"}
        mock_get_service.return_value = mock_service

        request = DeleteTodosRequest(session_id="test-session-789")
        dumped = request.model_dump()
        assert "session_id" in dumped
        assert dumped["session_id"] == "test-session-789"
