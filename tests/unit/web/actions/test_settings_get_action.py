"""Unit tests for SettingsGetAction."""

from unittest.mock import MagicMock, patch

from pipe.web.action_responses import SettingsResponse
from pipe.web.actions.settings.settings_get_action import SettingsGetAction


class TestSettingsGetAction:
    """Tests for SettingsGetAction."""

    @patch("pipe.web.actions.settings.settings_get_action.get_settings")
    def test_execute_success(self, mock_get_settings: MagicMock) -> None:
        """Test successful execution of SettingsGetAction.

        It should call get_settings(), call to_api_dict() on the settings object,
        and return a SettingsResponse.
        """
        # Setup mock settings
        mock_settings = MagicMock()
        mock_api_dict = {
            "model": "test-model",
            "search_model": "test-search-model",
            "context_limit": 1000,
            "cache_update_threshold": 10,
            "api_mode": "test-mode",
            "language": "en",
            "yolo": False,
            "max_tool_calls": 5,
            "expert_mode": True,
            "sessions_path": ".sessions",
            "reference_ttl": 3,
            "tool_response_expiration": 3600,
            "timezone": "UTC",
            "hyperparameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
            },
        }
        mock_settings.to_api_dict.return_value = mock_api_dict
        mock_get_settings.return_value = mock_settings

        # Execute action
        action = SettingsGetAction()
        response = action.execute()

        # Verify
        assert isinstance(response, SettingsResponse)
        assert response.settings.model == "test-model"
        assert response.settings.timezone == "UTC"
        assert response.settings.hyperparameters.temperature == 0.7

        mock_get_settings.assert_called_once()
        mock_settings.to_api_dict.assert_called_once()
