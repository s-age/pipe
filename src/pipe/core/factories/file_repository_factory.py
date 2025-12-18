"""
Factory for creating file repository instances based on configuration.
"""

from pipe.core.factories.settings_factory import SettingsFactory
from pipe.core.repositories.file_repository import FileRepository
from pipe.core.repositories.filesystem_repository import FileSystemRepository
from pipe.core.repositories.sandbox_file_repository import SandboxFileRepository
from pipe.core.utils.path import get_project_root


class FileRepositoryFactory:
    """
    Factory for creating appropriate file repository instances.
    """

    @staticmethod
    def create(
        project_root: str | None = None, enable_sandbox: bool | None = None
    ) -> FileRepository:
        """
        Create a file repository instance based on sandbox configuration.

        Args:
            project_root: The root directory for file operations.
                         If None (default), auto via get_project_root().
            enable_sandbox: Optional override for sandbox mode.
                          If None (default), reads from settings.
                          If True, SandboxFileRepository with restrictions.
                          If False, FileSystemRepository.

        Returns:
            FileRepository (SandboxFileRepository or FileSystemRepository)
        """
        # Auto-determine project_root if not provided
        if project_root is None:
            project_root = get_project_root()

        # Auto-load settings if enable_sandbox is not explicitly provided
        if enable_sandbox is None:
            try:
                settings = SettingsFactory.get_settings()
                enable_sandbox = settings.enable_sandbox
            except (FileNotFoundError, ValueError):
                # Settings not found (e.g., tests), default to sandbox
                enable_sandbox = True

        if enable_sandbox:
            return SandboxFileRepository(project_root)
        else:
            return FileSystemRepository(project_root)
