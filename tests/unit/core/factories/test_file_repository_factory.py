"""
Unit tests for FileRepositoryFactory.
"""

from unittest.mock import MagicMock, patch

from pipe.core.factories.file_repository_factory import FileRepositoryFactory


class TestFileRepositoryFactory:
    """Unit tests for FileRepositoryFactory."""

    @patch("pipe.core.factories.file_repository_factory.SandboxFileRepository")
    def test_create_with_explicit_params_sandbox_true(self, mock_sandbox_repo):
        """Test create with explicit project_root and enable_sandbox=True."""
        project_root = "/test/root"
        result = FileRepositoryFactory.create(
            project_root=project_root, enable_sandbox=True
        )

        mock_sandbox_repo.assert_called_once_with(project_root)
        assert result == mock_sandbox_repo.return_value

    @patch("pipe.core.factories.file_repository_factory.FileSystemRepository")
    def test_create_with_explicit_params_sandbox_false(self, mock_fs_repo):
        """Test create with explicit project_root and enable_sandbox=False."""
        project_root = "/test/root"
        result = FileRepositoryFactory.create(
            project_root=project_root, enable_sandbox=False
        )

        mock_fs_repo.assert_called_once_with(project_root)
        assert result == mock_fs_repo.return_value

    @patch("pipe.core.factories.file_repository_factory.get_project_root")
    @patch("pipe.core.factories.file_repository_factory.SandboxFileRepository")
    def test_create_auto_project_root(self, mock_sandbox_repo, mock_get_root):
        """Test create auto-determines project_root when None."""
        mock_get_root.return_value = "/auto/root"

        FileRepositoryFactory.create(project_root=None, enable_sandbox=True)

        mock_get_root.assert_called_once()
        mock_sandbox_repo.assert_called_once_with("/auto/root")

    @patch("pipe.core.factories.file_repository_factory.SettingsFactory.get_settings")
    @patch("pipe.core.factories.file_repository_factory.FileSystemRepository")
    def test_create_auto_sandbox_from_settings(self, mock_fs_repo, mock_get_settings):
        """Test create auto-determines enable_sandbox from settings."""
        mock_settings = MagicMock()
        mock_settings.enable_sandbox = False
        mock_get_settings.return_value = mock_settings

        FileRepositoryFactory.create(project_root="/test/root", enable_sandbox=None)

        mock_get_settings.assert_called_once()
        mock_fs_repo.assert_called_once_with("/test/root")

    @patch("pipe.core.factories.file_repository_factory.SettingsFactory.get_settings")
    @patch("pipe.core.factories.file_repository_factory.SandboxFileRepository")
    def test_create_auto_sandbox_fallback_on_error(
        self, mock_sandbox_repo, mock_get_settings
    ):
        """Test create defaults to sandbox=True when settings loading fails."""
        mock_get_settings.side_effect = FileNotFoundError("Settings not found")

        FileRepositoryFactory.create(project_root="/test/root", enable_sandbox=None)

        mock_get_settings.assert_called_once()
        mock_sandbox_repo.assert_called_once_with("/test/root")
