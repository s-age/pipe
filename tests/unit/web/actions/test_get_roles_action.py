"""Unit tests for GetRolesAction."""

from unittest.mock import MagicMock, patch

from pipe.core.models.role import RoleOption
from pipe.web.action_responses import RolesResponse
from pipe.web.actions.fs.get_roles_action import GetRolesAction


class TestGetRolesAction:
    """Unit tests for GetRolesAction."""

    @patch("pipe.web.actions.fs.get_roles_action.get_role_service")
    def test_execute_success(self, mock_get_role_service: MagicMock) -> None:
        """Test successful execution of GetRolesAction."""
        # Setup
        mock_service = MagicMock()
        mock_get_role_service.return_value = mock_service

        expected_roles = [
            RoleOption(label="Role 1", value="role1"),
            RoleOption(label="Role 2", value="role2"),
        ]
        mock_service.get_all_role_options.return_value = expected_roles

        action = GetRolesAction()

        # Execute
        result = action.execute()

        # Verify
        assert isinstance(result, RolesResponse)
        assert result.roles == expected_roles
        mock_service.get_all_role_options.assert_called_once()

    @patch("pipe.web.actions.fs.get_roles_action.get_role_service")
    def test_execute_empty(self, mock_get_role_service: MagicMock) -> None:
        """Test execution when no roles are available."""
        # Setup
        mock_service = MagicMock()
        mock_get_role_service.return_value = mock_service
        mock_service.get_all_role_options.return_value = []

        action = GetRolesAction()

        # Execute
        result = action.execute()

        # Verify
        assert isinstance(result, RolesResponse)
        assert result.roles == []
        mock_service.get_all_role_options.assert_called_once()
