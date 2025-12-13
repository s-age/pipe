import os

from pipe.core.models.settings import Settings
from pipe.core.utils.file import read_yaml_file


class SettingsFactory:
    """Factory for creating Settings instances."""

    @staticmethod
    def get_settings(project_root: str) -> Settings:
        """
        Loads the settings from the configuration file.
        Prioritizes 'setting.yml' over 'setting.default.yml'.
        """
        config_path = os.path.join(project_root, "setting.yml")
        if not os.path.exists(config_path):
            config_path = os.path.join(project_root, "setting.default.yml")

        if not os.path.exists(config_path):
            raise FileNotFoundError("Could not find setting.yml or setting.default.yml")

        config_data = read_yaml_file(config_path)
        return Settings(**config_data)
