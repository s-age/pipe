"""Unit tests for GetTurnsRequest."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.get_turns import GetTurnsRequest
from pydantic import ValidationError


class TestGetTurnsRequest:
    """Tests for the GetTurnsRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_request(self, mock_get_service: MagicMock) -> None:
        """Test initialization with valid session_id and since."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-session"}

        request = GetTurnsRequest(session_id="test-session", since=5)
        assert request.session_id == "test-session"
        assert request.since == 5
        mock_service.get_session.assert_called_once_with("test-session")

    @patch("pipe.web.service_container.get_session_service")
    def test_default_since(self, mock_get_service: MagicMock) -> None:
        """Test that since defaults to 0."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-session"}

        request = GetTurnsRequest(session_id="test-session")
        assert request.since == 0

    @patch("pipe.web.service_container.get_session_service")
    def test_session_not_found(self, mock_get_service: MagicMock) -> None:
        """Test that NotFoundError is raised if session does not exist."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = None

        with pytest.raises(NotFoundError, match="Session not found."):
            GetTurnsRequest(session_id="non-existent")

    def test_missing_session_id(self) -> None:
        """Test that missing session_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GetTurnsRequest(since=0)  # type: ignore[call-arg]

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("session_id",) and error["type"] == "missing"
            for error in errors
        )

    @patch("pipe.web.service_container.get_session_service")
    def test_negative_since(self, mock_get_service: MagicMock) -> None:
        """Test that negative since raises ValidationError."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-session"}

        with pytest.raises(ValidationError) as exc_info:
            GetTurnsRequest(session_id="test-session", since=-1)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("since",) and error["type"] == "greater_than_equal"
            for error in errors
        )

    @patch("pipe.web.service_container.get_session_service")
    def test_create_with_path_params(self, mock_get_service: MagicMock) -> None:
        """Test creating request with path parameters and body data."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-session"}

        path_params = {"session_id": "test-session"}
        body_data = {"since": 10}

        request = GetTurnsRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )

        assert request.session_id == "test-session"
        assert request.since == 10

    @patch("pipe.web.service_container.get_session_service")
    def test_normalize_camel_case(self, mock_get_service: MagicMock) -> None:
        """Test that camelCase keys are normalized to snake_case."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_session.return_value = {"session_id": "test-session"}

        # BaseRequest handles normalization via normalize_and_merge validator
        data = {"sessionId": "test-session", "since": 5}
        request = GetTurnsRequest.model_validate(data)

        assert request.session_id == "test-session"
        assert request.since == 5
