from unittest.mock import patch

import pytest
import yaml
from pipe.core.models.settings import Settings
from pipe.core.repositories.settings_repository import SettingsRepository


@pytest.fixture
def settings_data():
    """Minimal settings data for testing."""
    return {
        "model_configs": [
            {
                "name": "gemini-2.5-flash",
                "context_limit": 1000000,
                "cache_update_threshold": 20000,
            }
        ],
        "model": "gemini-2.5-flash",
        "search_model": "gemini-2.5-flash",
        "parameters": {
            "temperature": {"value": 0.1, "description": "desc"},
            "top_p": {"value": 0.5, "description": "desc"},
            "top_k": {"value": 10, "description": "desc"},
        },
    }


@pytest.fixture
def mock_project_root(tmp_path):
    """Mock get_project_root to return a temporary directory."""

    patch_path = "pipe.core.repositories.settings_repository.get_project_root"

    with patch(patch_path, return_value=str(tmp_path)):
        yield tmp_path


@pytest.fixture
def repository(mock_project_root):
    """Create a SettingsRepository instance."""

    return SettingsRepository()


class TestSettingsRepositoryLoad:
    """Test SettingsRepository.load() method."""

    def test_load_from_setting_yml(self, repository, mock_project_root, settings_data):
        """Test loading from setting.yml (prioritized)."""

        # Create setting.yml

        config_path = mock_project_root / "setting.yml"

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(settings_data, f)

        # Also create setting.default.yml to ensure setting.yml is prioritized

        default_config_path = mock_project_root / "setting.default.yml"

        with open(default_config_path, "w", encoding="utf-8") as f:
            yaml.dump({"model": "wrong-model"}, f)

        settings = repository.load()

        # After load, 'model' becomes a ModelConfig object

        assert settings.model.name == "gemini-2.5-flash"

        assert repository._cache is not None

    def test_load_from_setting_default_yml(
        self, repository, mock_project_root, settings_data
    ):
        """Test loading from setting.default.yml when setting.yml is missing."""

        config_path = mock_project_root / "setting.default.yml"

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(settings_data, f)

        settings = repository.load()

        assert settings.model.name == "gemini-2.5-flash"

    def test_load_file_not_found(self, repository):
        """Test that load() raises FileNotFoundError if no config file exists."""

        with pytest.raises(FileNotFoundError, match="Could not find setting.yml"):
            repository.load()

    def test_load_uses_cache(self, repository, mock_project_root, settings_data):
        """Test that subsequent load() calls return the cached object."""

        config_path = mock_project_root / "setting.yml"

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(settings_data, f)

        settings1 = repository.load()

        settings2 = repository.load()

        assert settings1 is settings2


class TestSettingsRepositorySave:
    """Test SettingsRepository.save() method."""

    def test_save_creates_setting_yml(
        self, repository, mock_project_root, settings_data
    ):
        """Test that save() creates setting.yml and updates cache."""

        settings = Settings(**settings_data)

        repository.save(settings)

        config_path = mock_project_root / "setting.yml"

        assert config_path.exists()

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Verify saved data (it uses model_dump(mode="json") which uses field names)

        assert data["model"]["name"] == "gemini-2.5-flash"

        assert repository._cache is settings


class TestSettingsRepositoryCache:
    """Test cache management methods."""

    def test_clear_cache(self, repository, mock_project_root, settings_data):
        """Test that clear_cache() resets the internal cache."""
        config_path = mock_project_root / "setting.yml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(settings_data, f)

        repository.load()
        assert repository._cache is not None

        repository.clear_cache()
        assert repository._cache is None

    def test_reload(self, repository, mock_project_root, settings_data):
        """Test that reload() bypasses the cache."""
        config_path = mock_project_root / "setting.yml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(settings_data, f)

        settings1 = repository.load()

        # Update file directly
        settings_data["api_mode"] = "new-mode"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(settings_data, f)

        settings2 = repository.reload()
        assert settings1 is not settings2
        assert settings2.api_mode == "new-mode"
        assert repository._cache is settings2
