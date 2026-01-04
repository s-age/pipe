"""Tests for SessionManagementController."""

from unittest.mock import MagicMock, Mock

import pytest
from pipe.core.collections.backup_files import SessionSummary
from pipe.web.action_responses import (
    BackupListResponse,
    SessionOverview,
    SessionTreeNode,
    SessionTreeResponse,
)
from pipe.web.controllers.session_management_controller import (
    SessionManagementController,
)
from pipe.web.exceptions import HttpException
from pipe.web.responses import ApiResponse
from pipe.web.responses.session_management_responses import (
    ArchiveSession,
    DashboardResponse,
)


class TestSessionManagementController:
    """Tests for the SessionManagementController class."""

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
        """Create a SessionManagementController instance with mocked dependencies."""
        return SessionManagementController(
            session_service=mock_session_service, settings=mock_settings
        )

    def test_initialization(self, mock_session_service, mock_settings):
        """Test that the controller can be initialized."""
        controller = SessionManagementController(
            session_service=mock_session_service, settings=mock_settings
        )
        assert controller.session_service == mock_session_service
        assert controller.settings == mock_settings

    def test_get_dashboard_success(self, controller, monkeypatch):
        """Test getting dashboard successfully."""
        # Mock SessionTreeAction
        overview = SessionOverview(
            session_id="active-1",
            purpose="Active purpose",
            created_at="2024-01-01T10:00:00",
            last_updated_at="2024-01-01T11:00:00",
        )
        tree_node = SessionTreeNode(session_id="active-1", overview=overview)
        mock_tree_response = SessionTreeResponse(
            sessions={"active-1": overview}, session_tree=[tree_node]
        )

        mock_tree_action = MagicMock()
        mock_tree_action.execute.return_value = mock_tree_response
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        # Mock SessionsListBackupAction
        session_summary = SessionSummary(
            session_id="session-1",
            file_path="path/to/session-1.json",
            purpose="Test purpose",
            deleted_at="2024-01-02T12:00:00",
            session_data={
                "purpose": "Test purpose",
                "background": "Test background",
                "roles": ["role1"],
                "procedure": "proc1",
                "artifacts": ["art1"],
                "multi_step_reasoning_enabled": True,
                "token_count": 123,
                "last_updated": "2024-01-01T12:00:00",
            },
        )

        mock_archives_response = BackupListResponse(sessions=[session_summary])
        mock_archives_action = MagicMock()
        mock_archives_action.execute.return_value = mock_archives_response
        mock_archives_action_class = Mock(return_value=mock_archives_action)

        # Patch the action classes
        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionsListBackupAction",
            mock_archives_action_class,
        )

        response, status_code = controller.get_dashboard()

        assert status_code == 200
        assert isinstance(response, ApiResponse)
        assert response.success is True
        assert isinstance(response.data, DashboardResponse)
        assert len(response.data.session_tree) == 1
        assert response.data.session_tree[0].session_id == "active-1"
        assert len(response.data.archives) == 1

        archive = response.data.archives[0]
        assert isinstance(archive, ArchiveSession)
        assert archive.session_id == "session-1"
        assert archive.file_path == "path/to/session-1.json"
        assert archive.purpose == "Test purpose"
        assert archive.background == "Test background"
        assert archive.roles == ["role1"]
        assert archive.procedure == "proc1"
        assert archive.artifacts == ["art1"]
        assert archive.multi_step_reasoning_enabled is True
        assert archive.token_count == 123
        assert archive.last_updated_at == "2024-01-01T12:00:00"
        assert archive.deleted_at == "2024-01-02T12:00:00"

        # Verify actions were called with correct params
        mock_tree_action_class.assert_called_once_with(params={}, request_data=None)
        mock_archives_action_class.assert_called_once_with(params={}, request_data=None)

    def test_get_dashboard_multi_step_reasoning_none_handling(
        self, controller, monkeypatch
    ):
        """Test that None value for multi_step_reasoning_enabled is handled as False."""
        # Mock SessionTreeAction
        mock_tree_action = MagicMock()
        mock_tree_action.execute.return_value = SessionTreeResponse(
            sessions={}, session_tree=[]
        )

        # Mock SessionsListBackupAction with None for multi_step_reasoning_enabled
        session_summary = SessionSummary(
            session_id="session-1",
            file_path="path/to/session-1.json",
            purpose=None,
            deleted_at=None,
            session_data={"multi_step_reasoning_enabled": None},
        )

        mock_archives_action = MagicMock()
        mock_archives_action.execute.return_value = BackupListResponse(
            sessions=[session_summary]
        )

        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionTreeAction",
            Mock(return_value=mock_tree_action),
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionsListBackupAction",
            Mock(return_value=mock_archives_action),
        )

        response, _ = controller.get_dashboard()
        assert response.success is True
        assert response.data.archives[0].multi_step_reasoning_enabled is False

    def test_get_dashboard_missing_session_data_handling(self, controller, monkeypatch):
        """Test handling of missing session_data or fields."""
        # Mock SessionTreeAction
        mock_tree_action = MagicMock()
        mock_tree_action.execute.return_value = SessionTreeResponse(
            sessions={}, session_tree=[]
        )

        # Mock SessionsListBackupAction with missing session_data
        session_summary = SessionSummary(
            session_id="session-1",
            file_path="path/to/session-1.json",
            purpose=None,
            deleted_at=None,
            session_data={},  # Empty dict
        )

        mock_archives_action = MagicMock()
        mock_archives_action.execute.return_value = BackupListResponse(
            sessions=[session_summary]
        )

        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionTreeAction",
            Mock(return_value=mock_tree_action),
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionsListBackupAction",
            Mock(return_value=mock_archives_action),
        )

        response, _ = controller.get_dashboard()
        assert response.success is True
        archive = response.data.archives[0]
        assert archive.session_id == "session-1"
        assert archive.purpose == ""
        assert archive.multi_step_reasoning_enabled is False
        assert archive.token_count == 0

    def test_get_dashboard_http_exception(self, controller, monkeypatch):
        """Test handling of HttpException from actions."""
        mock_tree_action = MagicMock()
        error = HttpException("Action failed")
        error.status_code = 400
        mock_tree_action.execute.side_effect = error

        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionTreeAction",
            Mock(return_value=mock_tree_action),
        )

        response, status_code = controller.get_dashboard()

        assert status_code == 400
        assert response.success is False
        assert response.message == "Action failed"

    def test_get_dashboard_generic_exception(self, controller, monkeypatch):
        """Test handling of generic Exception from actions."""
        mock_tree_action = MagicMock()
        mock_tree_action.execute.side_effect = Exception("Unexpected error")

        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionTreeAction",
            Mock(return_value=mock_tree_action),
        )

        response, status_code = controller.get_dashboard()

        assert status_code == 500
        assert response.success is False
        assert response.message == "Unexpected error"

    def test_get_dashboard_with_request_data(self, controller, monkeypatch):
        """Test that request_data is passed to actions."""
        mock_tree_action = MagicMock()
        mock_tree_action.execute.return_value = SessionTreeResponse(
            sessions={}, session_tree=[]
        )
        mock_tree_action_class = Mock(return_value=mock_tree_action)

        mock_archives_action = MagicMock()
        mock_archives_action.execute.return_value = BackupListResponse(sessions=[])
        mock_archives_action_class = Mock(return_value=mock_archives_action)

        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionTreeAction",
            mock_tree_action_class,
        )
        monkeypatch.setattr(
            "pipe.web.controllers.session_management_controller.SessionsListBackupAction",
            mock_archives_action_class,
        )

        mock_request = Mock()
        controller.get_dashboard(request_data=mock_request)

        mock_tree_action_class.assert_called_once_with(
            params={}, request_data=mock_request
        )
        mock_archives_action_class.assert_called_once_with(
            params={}, request_data=mock_request
        )
