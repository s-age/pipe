"""Unit tests for SessionStopAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.services.session_service import SessionService
from pipe.core.services.session_workflow_service import SessionWorkflowService
from pipe.web.actions.session.session_stop_action import SessionStopAction
from pipe.web.requests.sessions.stop_session import StopSessionRequest


class TestSessionStopAction:
    """Tests for SessionStopAction."""

    @pytest.fixture
    def mock_session_service(self) -> MagicMock:
        """Create a mock SessionService."""
        service = MagicMock(spec=SessionService)
        service.project_root = "/mock/project/root"
        return service

    @pytest.fixture
    def mock_workflow_service(self) -> MagicMock:
        """Create a mock SessionWorkflowService."""
        return MagicMock(spec=SessionWorkflowService)

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock StopSessionRequest."""
        request = MagicMock(spec=StopSessionRequest)
        request.session_id = "test-session-123"
        return request

    def test_init(
        self,
        mock_session_service: MagicMock,
        mock_workflow_service: MagicMock,
        mock_request: MagicMock,
    ):
        """Test initialization of SessionStopAction."""
        action = SessionStopAction(
            session_service=mock_session_service,
            session_workflow_service=mock_workflow_service,
            validated_request=mock_request,
        )

        assert action.session_service == mock_session_service
        assert action.session_workflow_service == mock_workflow_service
        assert action.validated_request == mock_request

    @patch("pipe.web.actions.session.session_stop_action.SessionStopResponse")
    def test_execute_success(
        self,
        MockResponse: MagicMock,
        mock_session_service: MagicMock,
        mock_workflow_service: MagicMock,
        mock_request: MagicMock,
    ):
        """Test successful execution of SessionStopAction."""
        action = SessionStopAction(
            session_service=mock_session_service,
            session_workflow_service=mock_workflow_service,
            validated_request=mock_request,
        )

        # Execute
        response = action.execute()

        # Verify delegation
        mock_workflow_service.stop_session.assert_called_once_with(
            "test-session-123", "/mock/project/root"
        )

        # Verify response creation
        MockResponse.assert_called_once_with(
            message="Session test-session-123 stopped and transaction rolled back.",
            session_id="test-session-123",
        )
        assert response == MockResponse.return_value

    def test_execute_no_request(
        self,
        mock_session_service: MagicMock,
        mock_workflow_service: MagicMock,
    ):
        """Test execution raises ValueError when request is missing."""
        action = SessionStopAction(
            session_service=mock_session_service,
            session_workflow_service=mock_workflow_service,
            validated_request=None,
        )

        with pytest.raises(ValueError, match="Request is required"):
            action.execute()
