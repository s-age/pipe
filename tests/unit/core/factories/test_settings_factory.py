"""Unit tests for SettingsFactory."""

from unittest.mock import MagicMock, patch

from pipe.core.factories.settings_factory import SettingsFactory

from tests.factories.models.settings_factory import create_test_settings


class TestSettingsFactory:
    """Tests for SettingsFactory."""

    @patch("pipe.core.factories.settings_factory.SettingsRepository")
    def test_get_settings_success(self, MockSettingsRepository: MagicMock) -> None:
        """Test that get_settings correctly uses SettingsRepository to load settings."""
        # Setup
        mock_repo_instance = MockSettingsRepository.return_value
        expected_settings = create_test_settings()
        mock_repo_instance.load.return_value = expected_settings

        # Execute
        result = SettingsFactory.get_settings()

        # Verify
        assert result == expected_settings
        MockSettingsRepository.assert_called_once()
        mock_repo_instance.load.assert_called_once()
