"""Tests for SessionGetAction."""

from unittest.mock import MagicMock

import pytest
from pipe.core.services.session_service import SessionService
from pipe.web.actions.session.session_get_action import SessionGetAction
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.get_session import GetSessionRequest

from tests.factories.models import SessionFactory


class TestSessionGetAction:
    """Tests for SessionGetAction."""

    @pytest.fixture
    def mock_session_service(self) -> MagicMock:
        """Fixture for mocked SessionService."""
        return MagicMock(spec=SessionService)

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Fixture for mocked GetSessionRequest."""
        request = MagicMock(spec=GetSessionRequest)
        request.session_id = "test-session-id"
        return request

    def test_init(
        self, mock_session_service: MagicMock, mock_request: MagicMock
    ) -> None:
        """Test initialization of SessionGetAction."""
        action = SessionGetAction(
            session_service=mock_session_service, validated_request=mock_request
        )
        assert action.session_service == mock_session_service
        assert action.validated_request == mock_request

    def test_execute_success(
        self, mock_session_service: MagicMock, mock_request: MagicMock
    ) -> None:
        """Test successful execution of SessionGetAction."""
        # Arrange
        expected_session = SessionFactory.create(session_id="test-session-id")
        mock_session_service.get_session.return_value = expected_session

        action = SessionGetAction(
            session_service=mock_session_service, validated_request=mock_request
        )

        # Act
        result = action.execute()

        # Assert
        assert result == expected_session
        mock_session_service.get_session.assert_called_once_with("test-session-id")

    def test_execute_not_found(
        self, mock_session_service: MagicMock, mock_request: MagicMock
    ) -> None:
        """Test execution when session is not found."""
        # Arrange
        mock_session_service.get_session.return_value = None

        action = SessionGetAction(
            session_service=mock_session_service, validated_request=mock_request
        )

        # Act & Assert
        with pytest.raises(NotFoundError, match="Session 'test-session-id' not found"):
            action.execute()

        mock_session_service.get_session.assert_called_once_with("test-session-id")

    def test_execute_missing_request(self, mock_session_service: MagicMock) -> None:
        """Test execution when validated_request is missing."""
        # Arrange
        action = SessionGetAction(
            session_service=mock_session_service, validated_request=None
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Request is required"):
            action.execute()
