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
    def get_settings() -> Settings:
        """
        Loads the settings from the configuration file.
        Prioritizes 'setting.yml' over 'setting.default.yml'.

        Returns:
            A validated Settings model instance.

        Note:
            This method now delegates to SettingsRepository. The project root
            is automatically detected using get_project_root(). Results are
            cached within the repository instance created for this call.
        """
        repository = SettingsRepository()
        return repository.load()
