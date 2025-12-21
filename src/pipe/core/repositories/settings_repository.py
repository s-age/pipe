"""
Repository for managing Settings persistence.

Provides centralized access to application settings loaded from YAML configuration
files, following the repository pattern used throughout the codebase.
"""

import os

from pipe.core.models.settings import Settings
from pipe.core.repositories.file_repository import FileRepository
from pipe.core.utils.file import read_yaml_file
from pipe.core.utils.path import get_project_root


class SettingsRepository(FileRepository):
    """
    Handles loading and caching of Settings from YAML configuration files.

    This repository:
    - Loads settings from setting.yml or setting.default.yml
    - Provides caching to avoid repeated file I/O
    - Validates settings using the Settings Pydantic model
    - Automatically determines project_root using get_project_root()

    Usage:
        repo = SettingsRepository()
        settings = repo.load()
    """

    def __init__(self):
        """
        Initialize the settings repository.

        The project root is automatically detected using get_project_root().
        """
        super().__init__()
        self.project_root = get_project_root()
        self._cache: Settings | None = None

    def load(self, use_cache: bool = True) -> Settings:
        """
        Load settings from the YAML configuration file.

        Prioritizes 'setting.yml' over 'setting.default.yml'. Results are cached
        by default to avoid repeated file I/O operations.

        Args:
            use_cache: If True, returns cached settings if available. If False,
                always reloads from the file system.

        Returns:
            A validated Settings model instance.

        Raises:
            FileNotFoundError: If neither setting.yml nor setting.default.yml exists.
        """
        if use_cache and self._cache is not None:
            return self._cache

        config_path = self._get_config_path()
        config_data = read_yaml_file(config_path)
        settings = Settings(**config_data)

        self._cache = settings
        return settings

    def save(self, settings: Settings) -> None:
        """
        Save settings to setting.yml.

        Note: This method is provided for completeness but is rarely used in
        practice, as settings are typically managed manually via YAML files.

        Args:
            settings: The Settings model instance to save.
        """
        import yaml

        config_path = os.path.join(self.project_root, "setting.yml")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # Convert Settings model to dict for YAML serialization
        settings_dict = settings.model_dump(mode="json")

        with open(config_path, "w") as f:
            yaml.dump(settings_dict, f, default_flow_style=False, allow_unicode=True)

        # Update cache
        self._cache = settings

    def clear_cache(self) -> None:
        """
        Clear the cached settings.

        Useful when you need to force a reload from the file system, for example
        after external modification of the configuration file.
        """
        self._cache = None

    def reload(self) -> Settings:
        """
        Reload settings from the file system, bypassing cache.

        Convenience method equivalent to load(use_cache=False).

        Returns:
            A freshly loaded Settings model instance.
        """
        return self.load(use_cache=False)

    def _get_config_path(self) -> str:
        """
        Determine the path to the configuration file.

        Prioritizes 'setting.yml' over 'setting.default.yml'.

        Returns:
            The absolute path to the configuration file.

        Raises:
            FileNotFoundError: If neither configuration file exists.
        """
        config_path = os.path.join(self.project_root, "setting.yml")
        if not os.path.exists(config_path):
            config_path = os.path.join(self.project_root, "setting.default.yml")

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Could not find setting.yml or setting.default.yml in "
                f"{self.project_root}"
            )

        return config_path
