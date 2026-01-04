"""Unit tests for GetSessionRequest."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.get_session import GetSessionRequest
from pydantic import ValidationError


class TestGetSessionRequest:
    """Tests for GetSessionRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    def test_validate_session_exists_success(self, mock_get_service: MagicMock) -> None:
        """Test successful validation when session exists."""
        # Setup mock
        mock_service = MagicMock()
        mock_service.get_session.return_value = {"session_id": "test-123"}
        mock_get_service.return_value = mock_service

        # Execute
        request = GetSessionRequest(session_id="test-123")

        # Verify
        assert request.session_id == "test-123"
        mock_service.get_session.assert_called_once_with("test-123")

    @patch("pipe.web.service_container.get_session_service")
    def test_validate_session_exists_not_found(
        self, mock_get_service: MagicMock
    ) -> None:
        """Test validation failure when session does not exist."""
        # Setup mock
        mock_service = MagicMock()
        mock_service.get_session.return_value = None
        mock_get_service.return_value = mock_service

        # Execute & Verify
        with pytest.raises(NotFoundError, match="Session not found."):
            GetSessionRequest(session_id="non-existent")

        mock_service.get_session.assert_called_once_with("non-existent")

    def test_path_params_definition(self) -> None:
        """Test that path_params is correctly defined."""
        assert GetSessionRequest.path_params == ["session_id"]

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service: MagicMock) -> None:
        """Test creation using path parameters."""
        # Setup mock
        mock_service = MagicMock()
        mock_service.get_session.return_value = {"session_id": "test-456"}
        mock_get_service.return_value = mock_service

        # Execute
        request = GetSessionRequest.create_with_path_params(
            path_params={"session_id": "test-456"}, body_data={}
        )

        # Verify
        assert isinstance(request, GetSessionRequest)
        assert request.session_id == "test-456"

    def test_missing_session_id_raises_validation_error(self) -> None:
        """Test that missing session_id raises ValidationError (Pydantic level)."""
        # Note: This fails before the model_validator runs because session_id is required
        with pytest.raises(ValidationError):
            GetSessionRequest.model_validate({})
