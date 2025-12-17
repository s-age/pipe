from pipe.core.models.settings import Settings
from pipe.core.repositories.settings_repository import SettingsRepository


class SettingsFactory:
    """
    Factory for creating Settings instances.

    Note: This factory now uses SettingsRepository internally. For new code,
    consider using SettingsRepository directly for better testability and
    more control over caching behavior.
    """

    @staticmethod
    def get_settings(project_root: str) -> Settings:
        """
        Loads the settings from the configuration file.
        Prioritizes 'setting.yml' over 'setting.default.yml'.

        Args:
            project_root: The root directory of the project.

        Returns:
            A validated Settings model instance.

        Note:
            This method now delegates to SettingsRepository. Results are cached
            within the repository instance created for this call.
        """
        repository = SettingsRepository(project_root=project_root)
        return repository.load()
