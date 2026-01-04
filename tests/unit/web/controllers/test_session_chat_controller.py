"""Tests for SessionChatController."""

from unittest.mock import Mock

import pytest
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import Session
from pipe.web.action_responses import (
    SessionOverview,
    SessionTreeNode,
    SessionTreeResponse,
    SettingsInfo,
    SettingsResponse,
)
from pipe.web.controllers.session_chat_controller import SessionChatController
from pipe.web.exceptions import HttpException, NotFoundError
from pipe.web.responses import ApiResponse
from pipe.web.responses.session_chat_responses import ChatContextResponse


class TestSessionChatController:
    """Tests for the SessionChatController class."""

    @pytest.fixture
    def mock_session_service(self):
        """Create a mock session service."""
        return Mock()

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return Mock()

    @pytest.fixture
    def controller(self, mock_session_service, mock_settings):
        """Create a SessionChatController instance with mocked dependencies."""
        return SessionChatController(
            session_service=mock_session_service, settings=mock_settings
        )

    @pytest.fixture
    def sample_session_tree_response(self):
        """Create a sample session tree response."""
        overview = SessionOverview(
            session_id="session-1",
            purpose="Test session",
            created_at="2024-01-01T00:00:00",
            last_updated_at="2024-01-01T01:00:00",
        )
        tree_node = SessionTreeNode(session_id="session-1", overview=overview)
        return SessionTreeResponse(
            sessions={"session-1": overview}, session_tree=[tree_node]
        )

    @pytest.fixture
    def sample_settings_response(self):
        """Create a sample settings response."""
        settings_info = SettingsInfo(
            model="claude-3-sonnet",
            search_model="claude-3-haiku",
            context_limit=100000,
            cache_update_threshold=1000,
            api_mode="api",
            language="en",
            yolo=False,
            max_tool_calls=50,
            expert_mode=False,
            sessions_path="/path/to/sessions",
            reference_ttl=3600,
            tool_response_expiration=300,
            timezone="UTC",
            hyperparameters=Hyperparameters(temperature=1.0, top_k=0, top_p=0.999),
        )
        return SettingsResponse(settings=settings_info)

    @pytest.fixture
    def sample_session(self):
        """Create a sample session."""
        return Session(
            session_id="session-1",
            created_at="2024-01-01T00:00:00",
            purpose="Test Session",
            roles=["test-role"],
        )

    def test_initialization(self, mock_session_service, mock_settings):
        """Test that the controller can be initialized."""
        controller = SessionChatController(
            session_service=mock_session_service, settings=mock_settings
        )
        assert controller.session_service == mock_session_service
        assert controller.settings == mock_settings

    def test_get_chat_context_without_session_id(
        self,
        controller,
        sample_session_tree_response,
        sample_settings_response,
        monkeypatch,
    ):
        """Test getting chat context without a specific session ID."""
        # Mock SessionTreeAction
        mock_tree_action = Mock()
        mock_tree_action.execute.return_value = sample_session_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SettingsGetAction
        mock_settings_action = Mock()
        mock_settings_action.execute.return_value = sample_settings_response
        mock_settings_action_class = Mock(return_value=mock_settings_action)

        # Patch the action classes
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SettingsGetAction",
            mock_settings_action_class,
        )

        response, status_code = controller.get_chat_context(session_id=None)

        assert status_code == 200
        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert isinstance(response.data, ChatContextResponse)
        assert response.data.sessions == sample_session_tree_response.sessions
        assert response.data.session_tree == sample_session_tree_response.session_tree
        assert response.data.settings == sample_settings_response.settings
        assert response.data.current_session is None

    def test_get_chat_context_with_valid_session_id(
        self,
        controller,
        sample_session_tree_response,
        sample_settings_response,
        sample_session,
        monkeypatch,
    ):
        """Test getting chat context with a valid session ID."""
        # Mock SessionTreeAction
        mock_tree_action = Mock()
        mock_tree_action.execute.return_value = sample_session_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SettingsGetAction
        mock_settings_action = Mock()
        mock_settings_action.execute.return_value = sample_settings_response
        mock_settings_action_class = Mock(return_value=mock_settings_action)

        # Mock dispatch_action to return session data
        mock_dispatch = Mock(return_value=({"data": sample_session}, 200))

        # Patch the action classes and dispatch_action
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SettingsGetAction",
            mock_settings_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.dispatch_action",
            mock_dispatch,
        )

        response, status_code = controller.get_chat_context(session_id="session-1")

        assert status_code == 200
        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert isinstance(response.data, ChatContextResponse)
        assert response.data.current_session == sample_session
        mock_dispatch.assert_called_once()

    def test_get_chat_context_with_nonexistent_session_id(
        self,
        controller,
        sample_session_tree_response,
        sample_settings_response,
        monkeypatch,
    ):
        """Test getting chat context with a nonexistent session ID still returns tree and settings."""
        # Mock SessionTreeAction
        mock_tree_action = Mock()
        mock_tree_action.execute.return_value = sample_session_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SettingsGetAction
        mock_settings_action = Mock()
        mock_settings_action.execute.return_value = sample_settings_response
        mock_settings_action_class = Mock(return_value=mock_settings_action)

        # Mock dispatch_action to raise NotFoundError
        def mock_dispatch_raises(*args, **kwargs):
            raise NotFoundError("Session not found")

        # Patch the action classes and dispatch_action
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SettingsGetAction",
            mock_settings_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.dispatch_action",
            mock_dispatch_raises,
        )

        response, status_code = controller.get_chat_context(
            session_id="nonexistent-session"
        )

        # Should still return 200 with tree and settings, but no current_session
        assert status_code == 200
        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert isinstance(response.data, ChatContextResponse)
        assert response.data.sessions == sample_session_tree_response.sessions
        assert response.data.session_tree == sample_session_tree_response.session_tree
        assert response.data.settings == sample_settings_response.settings
        assert response.data.current_session is None

    def test_get_chat_context_with_session_non_200_status(
        self,
        controller,
        sample_session_tree_response,
        sample_settings_response,
        monkeypatch,
    ):
        """Test getting chat context when session fetch returns non-200 status."""
        # Mock SessionTreeAction
        mock_tree_action = Mock()
        mock_tree_action.execute.return_value = sample_session_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SettingsGetAction
        mock_settings_action = Mock()
        mock_settings_action.execute.return_value = sample_settings_response
        mock_settings_action_class = Mock(return_value=mock_settings_action)

        # Mock dispatch_action to return 404 status
        mock_dispatch = Mock(return_value=({}, 404))

        # Patch the action classes and dispatch_action
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SettingsGetAction",
            mock_settings_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.dispatch_action",
            mock_dispatch,
        )

        response, status_code = controller.get_chat_context(session_id="session-1")

        # Should still return 200 with tree and settings, but no current_session
        assert status_code == 200
        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert response.data.current_session is None

    def test_get_chat_context_tree_action_raises_http_exception(
        self, controller, monkeypatch
    ):
        """Test that HttpException from tree action is handled properly."""
        # Mock SessionTreeAction to raise InternalServerError
        from pipe.web.exceptions import InternalServerError

        def mock_tree_action_raises(*args, **kwargs):
            raise InternalServerError("Tree error")

        mock_tree_action_instance = Mock()
        mock_tree_action_instance.execute = mock_tree_action_raises
        mock_tree_action_class = Mock(return_value=mock_tree_action_instance)

        # Patch the action class
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )

        response, status_code = controller.get_chat_context(session_id=None)

        assert status_code == 500
        assert isinstance(response, ApiResponse)
        assert response.success is False
        assert response.message == "Tree error"

    def test_get_chat_context_settings_action_raises_http_exception(
        self, controller, sample_session_tree_response, monkeypatch
    ):
        """Test that HttpException from settings action is handled properly."""
        # Mock SessionTreeAction
        mock_tree_action = Mock()
        mock_tree_action.execute.return_value = sample_session_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SettingsGetAction to raise a custom HttpException with status_code
        def mock_settings_action_raises(*args, **kwargs):
            error = HttpException("Settings error")
            error.status_code = 403
            raise error

        mock_settings_action_instance = Mock()
        mock_settings_action_instance.execute = mock_settings_action_raises
        mock_settings_action_class = Mock(return_value=mock_settings_action_instance)

        # Patch the action classes
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SettingsGetAction",
            mock_settings_action_class,
        )

        response, status_code = controller.get_chat_context(session_id=None)

        assert status_code == 403
        assert isinstance(response, ApiResponse)
        assert response.success is False
        assert response.message == "Settings error"

    def test_get_chat_context_generic_exception(
        self, controller, sample_session_tree_response, monkeypatch
    ):
        """Test that generic exceptions are handled with 500 status."""
        # Mock SessionTreeAction
        mock_tree_action = Mock()
        mock_tree_action.execute.return_value = sample_session_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SettingsGetAction to raise generic exception
        def mock_settings_action_raises(*args, **kwargs):
            raise ValueError("Unexpected error")

        mock_settings_action_instance = Mock()
        mock_settings_action_instance.execute = mock_settings_action_raises
        mock_settings_action_class = Mock(return_value=mock_settings_action_instance)

        # Patch the action classes
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SettingsGetAction",
            mock_settings_action_class,
        )

        response, status_code = controller.get_chat_context(session_id=None)

        assert status_code == 500
        assert isinstance(response, ApiResponse)
        assert response.success is False
        assert response.message == "Unexpected error"

    def test_get_chat_context_with_request_data(
        self,
        controller,
        sample_session_tree_response,
        sample_settings_response,
        monkeypatch,
    ):
        """Test that request_data is passed to actions."""
        # Mock SessionTreeAction
        mock_tree_action = Mock()
        mock_tree_action.execute.return_value = sample_session_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SettingsGetAction
        mock_settings_action = Mock()
        mock_settings_action.execute.return_value = sample_settings_response
        mock_settings_action_class = Mock(return_value=mock_settings_action)

        # Patch the action classes
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SettingsGetAction",
            mock_settings_action_class,
        )

        mock_request = Mock()
        response, status_code = controller.get_chat_context(
            session_id=None, request_data=mock_request
        )

        # Verify request_data was passed to actions
        mock_tree_action_class.assert_called_once_with(
            params={}, request_data=mock_request
        )
        mock_settings_action_class.assert_called_once_with(
            params={}, request_data=mock_request
        )
        assert status_code == 200

    def test_get_chat_context_with_request_data_and_session_id(
        self,
        controller,
        sample_session_tree_response,
        sample_settings_response,
        sample_session,
        monkeypatch,
    ):
        """Test that request_data is passed to dispatch_action when fetching session."""
        # Mock SessionTreeAction
        mock_tree_action = Mock()
        mock_tree_action.execute.return_value = sample_session_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SettingsGetAction
        mock_settings_action = Mock()
        mock_settings_action.execute.return_value = sample_settings_response
        mock_settings_action_class = Mock(return_value=mock_settings_action)

        # Mock dispatch_action
        mock_dispatch = Mock(return_value=({"data": sample_session}, 200))

        # Patch the action classes and dispatch_action
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.SettingsGetAction",
            mock_settings_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_chat_controller.dispatch_action",
            mock_dispatch,
        )

        mock_request = Mock()
        response, status_code = controller.get_chat_context(
            session_id="session-1", request_data=mock_request
        )

        # Verify request_data was passed to dispatch_action
        from pipe.web.actions import SessionGetAction

        mock_dispatch.assert_called_once_with(
            action=SessionGetAction,
            params={"session_id": "session-1"},
            request_data=mock_request,
        )
        assert status_code == 200
        assert response.data.current_session == sample_session
