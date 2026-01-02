from unittest.mock import Mock

import pytest
from pipe.core.models.role import RoleOption
from pipe.core.repositories.role_repository import RoleRepository
from pipe.core.services.role_service import RoleService


@pytest.fixture
def mock_repository():
    """Create a mock RoleRepository."""
    return Mock(spec=RoleRepository)


@pytest.fixture
def service(mock_repository):
    """Create a RoleService instance with mocked repository."""
    return RoleService(role_repository=mock_repository)


class TestRoleServiceInit:
    """Tests for RoleService.__init__."""

    def test_init(self, mock_repository):
        """Test that RoleService is initialized with the repository."""
        service = RoleService(role_repository=mock_repository)
        assert service.role_repository == mock_repository


class TestRoleServiceGetAllRoleOptions:
    """Tests for RoleService.get_all_role_options."""

    def test_get_all_role_options(self, service, mock_repository):
        """Test that get_all_role_options delegates to the repository."""
        expected_options = [
            RoleOption(label="Role 1", value="roles/role1.md"),
            RoleOption(label="Role 2", value="roles/role2.md"),
        ]
        mock_repository.get_all_role_options.return_value = expected_options

        result = service.get_all_role_options()

        assert result == expected_options
        mock_repository.get_all_role_options.assert_called_once()
