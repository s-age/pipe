"""Unit tests for StartSessionController."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.controllers.start_session_controller import StartSessionController
from pipe.web.exceptions import InternalServerError, NotFoundError
from pipe.web.responses import ApiResponse


class TestStartSessionController:
    """Tests for the StartSessionController class."""

    @pytest.fixture
    def mock_session_service(self):
        """Create a mock session service."""
        return MagicMock()

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        return MagicMock()

    @pytest.fixture
    def controller(self, mock_session_service, mock_settings):
        """Create a StartSessionController instance with mocked dependencies."""
        return StartSessionController(
            session_service=mock_session_service, settings=mock_settings
        )

    def test_initialization(self, mock_session_service, mock_settings):
        """Test that the controller can be initialized."""
        controller = StartSessionController(
            session_service=mock_session_service, settings=mock_settings
        )
        assert controller.session_service == mock_session_service
        assert controller.settings == mock_settings

    @patch("pipe.web.controllers.start_session_controller.SessionTreeAction")
    @patch("pipe.web.controllers.start_session_controller.SessionGetAction")
    @patch("pipe.web.controllers.start_session_controller.GetRolesAction")
    @patch("pipe.web.controllers.start_session_controller.SettingsGetAction")
    @patch("pipe.web.controllers.start_session_controller.StartSessionContextResponse")
    def test_get_session_with_tree_success(
        self,
        mock_context_response_class,
        mock_settings_action_class,
        mock_roles_action_class,
        mock_session_action_class,
        mock_tree_action_class,
        controller,
    ):
        """Test get_session_with_tree happy path."""
        # Setup mocks
        mock_tree_action = mock_tree_action_class.return_value
        mock_tree_action.execute.return_value = MagicMock(session_tree=[])

        mock_session_action = mock_session_action_class.return_value
        mock_session_action.execute.return_value = MagicMock()

        mock_roles_action = mock_roles_action_class.return_value
        mock_roles_action.execute.return_value = MagicMock(roles=[])

        mock_settings_action = mock_settings_action_class.return_value
        mock_settings_action.execute.return_value = MagicMock(settings=MagicMock())

        mock_context_response = mock_context_response_class.return_value

        # Execute
        response, status_code = controller.get_session_with_tree(
            session_id="test-session"
        )

        # Verify
        assert status_code == 200
        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert response.data == mock_context_response

        # Verify action calls
        mock_tree_action_class.assert_called_once_with(params={}, request_data=None)
        mock_session_action_class.assert_called_once_with(
            params={"session_id": "test-session"}, request_data=None
        )
        mock_roles_action_class.assert_called_once_with(params={}, request_data=None)
        mock_settings_action_class.assert_called_once_with(params={}, request_data=None)

    @patch("pipe.web.controllers.start_session_controller.SessionTreeAction")
    def test_get_session_with_tree_http_exception(
        self, mock_tree_action_class, controller
    ):
        """Test get_session_with_tree handling HttpException."""
        # Setup mock to raise HttpException
        mock_tree_action = mock_tree_action_class.return_value
        mock_tree_action.execute.side_effect = NotFoundError("Session not found")

        # Execute
        response, status_code = controller.get_session_with_tree(
            session_id="test-session"
        )

        # Verify
        assert status_code == 404
        assert isinstance(response, ApiResponse)
        assert response.success is False
        assert response.message == "Session not found"

    @patch("pipe.web.controllers.start_session_controller.SessionTreeAction")
    def test_get_session_with_tree_generic_exception(
        self, mock_tree_action_class, controller
    ):
        """Test get_session_with_tree handling generic Exception."""
        # Setup mock to raise generic Exception
        mock_tree_action = mock_tree_action_class.return_value
        mock_tree_action.execute.side_effect = Exception("Unexpected error")

        # Execute
        response, status_code = controller.get_session_with_tree(
            session_id="test-session"
        )

        # Verify
        assert status_code == 500
        assert isinstance(response, ApiResponse)
        assert response.success is False
        assert response.message == "Unexpected error"

    @patch("pipe.web.controllers.start_session_controller.SessionTreeAction")
    @patch("pipe.web.controllers.start_session_controller.SettingsGetAction")
    @patch("pipe.web.controllers.start_session_controller.GetRolesAction")
    @patch("pipe.web.controllers.start_session_controller.StartSessionContextResponse")
    def test_get_settings_with_tree_success(
        self,
        mock_context_response_class,
        mock_roles_action_class,
        mock_settings_action_class,
        mock_tree_action_class,
        controller,
    ):
        """Test get_settings_with_tree happy path."""
        # Setup mocks
        mock_tree_action = mock_tree_action_class.return_value
        mock_tree_action.execute.return_value = MagicMock(session_tree=[])

        mock_settings_action = mock_settings_action_class.return_value
        mock_settings_action.execute.return_value = MagicMock(settings=MagicMock())

        mock_roles_action = mock_roles_action_class.return_value
        mock_roles_action.execute.return_value = MagicMock(roles=[])

        mock_context_response = mock_context_response_class.return_value

        # Execute
        response, status_code = controller.get_settings_with_tree()

        # Verify
        assert status_code == 200
        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert response.data == mock_context_response

        # Verify action calls
        mock_tree_action_class.assert_called_once_with(params={}, request_data=None)
        mock_settings_action_class.assert_called_once_with(params={}, request_data=None)
        mock_roles_action_class.assert_called_once_with(params={}, request_data=None)

    @patch("pipe.web.controllers.start_session_controller.SessionTreeAction")
    def test_get_settings_with_tree_http_exception(
        self, mock_tree_action_class, controller
    ):
        """Test get_settings_with_tree handling HttpException."""
        # Setup mock to raise HttpException
        mock_tree_action = mock_tree_action_class.return_value
        mock_tree_action.execute.side_effect = InternalServerError("Server error")

        # Execute
        response, status_code = controller.get_settings_with_tree()

        # Verify
        assert status_code == 500
        assert isinstance(response, ApiResponse)
        assert response.success is False
        assert response.message == "Server error"

    @patch("pipe.web.controllers.start_session_controller.SessionTreeAction")
    def test_get_settings_with_tree_generic_exception(
        self, mock_tree_action_class, controller
    ):
        """Test get_settings_with_tree handling generic Exception."""
        # Setup mock to raise generic Exception
        mock_tree_action = mock_tree_action_class.return_value
        mock_tree_action.execute.side_effect = ValueError("Value error")

        # Execute
        response, status_code = controller.get_settings_with_tree()

        # Verify
        assert status_code == 500
        assert isinstance(response, ApiResponse)
        assert response.success is False
        assert response.message == "Value error"
