"""Unit tests for StopSessionRequest."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.stop_session import StopSessionRequest
from pydantic import ValidationError


class TestStopSessionRequest:
    """Tests for the StopSessionRequest model."""

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    def test_valid_session_running(self, mock_pm_class, mock_get_service):
        """Test validation passes when session exists and is running."""
        # Setup mocks
        mock_service = MagicMock()
        mock_service.project_root = "/mock/root"
        mock_service.get_session.return_value = MagicMock()
        mock_get_service.return_value = mock_service

        mock_pm = mock_pm_class.return_value
        mock_pm.is_running.return_value = True

        # Execute
        request = StopSessionRequest(session_id="test-session")

        # Verify
        assert request.session_id == "test-session"
        mock_service.get_session.assert_called_once_with("test-session")
        mock_pm_class.assert_called_once_with("/mock/root")
        mock_pm.is_running.assert_called_once_with("test-session")

    @patch("pipe.web.service_container.get_session_service")
    def test_session_not_found(self, mock_get_service):
        """Test NotFoundError is raised when session does not exist."""
        # Setup mocks
        mock_service = MagicMock()
        mock_service.get_session.return_value = None
        mock_get_service.return_value = mock_service

        # Execute and Verify
        with pytest.raises(NotFoundError, match="Session 'missing-session' not found."):
            StopSessionRequest(session_id="missing-session")

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    def test_session_not_running(self, mock_pm_class, mock_get_service):
        """Test BadRequestError is raised when session is not running."""
        # Setup mocks
        mock_service = MagicMock()
        mock_service.get_session.return_value = MagicMock()
        mock_get_service.return_value = mock_service

        mock_pm = mock_pm_class.return_value
        mock_pm.is_running.return_value = False

        # Execute and Verify
        with pytest.raises(
            BadRequestError, match="Session 'test-session' is not currently running."
        ):
            StopSessionRequest(session_id="test-session")

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    def test_normalize_keys(self, mock_pm_class, mock_get_service):
        """Test that camelCase keys are normalized to snake_case."""
        mock_service = MagicMock()
        mock_service.get_session.return_value = MagicMock()
        mock_get_service.return_value = mock_service
        mock_pm_class.return_value.is_running.return_value = True

        data = {"sessionId": "test-session"}
        request = StopSessionRequest.model_validate(data)
        assert request.session_id == "test-session"

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    def test_create_with_path_params(self, mock_pm_class, mock_get_service):
        """Test creating request with path parameters."""
        mock_service = MagicMock()
        mock_service.get_session.return_value = MagicMock()
        mock_get_service.return_value = mock_service
        mock_pm_class.return_value.is_running.return_value = True

        request = StopSessionRequest.create_with_path_params(
            path_params={"session_id": "path-session"}, body_data={}
        )
        assert request.session_id == "path-session"

    def test_missing_session_id(self):
        """Test validation error when session_id is missing."""
        with pytest.raises(ValidationError):
            StopSessionRequest.model_validate({})

    @patch("pipe.web.service_container.get_session_service")
    @patch("pipe.core.services.process_manager_service.ProcessManagerService")
    def test_extra_fields_forbidden(self, mock_pm_class, mock_get_service):
        """Test that extra fields are forbidden."""
        mock_service = MagicMock()
        mock_service.get_session.return_value = MagicMock()
        mock_get_service.return_value = mock_service
        mock_pm_class.return_value.is_running.return_value = True

        with pytest.raises(ValidationError) as exc_info:
            StopSessionRequest(session_id="test-session", extra_field="not_allowed")

        assert "extra_forbidden" in str(exc_info.value)
