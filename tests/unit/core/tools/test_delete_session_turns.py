from unittest.mock import MagicMock, patch

from pipe.core.models.results.delete_session_turns_result import (
    DeleteSessionTurnsResult,
)
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.delete_session_turns import delete_session_turns


class TestDeleteSessionTurns:
    """Tests for delete_session_turns tool."""

    @patch("pipe.core.tools.delete_session_turns.ServiceFactory")
    @patch("pipe.core.tools.delete_session_turns.SettingsFactory.get_settings")
    def test_delete_session_turns_success(
        self, mock_get_settings, mock_service_factory_class
    ):
        """Test successful deletion of session turns."""
        # Setup
        session_id = "test-session"
        turns = [1, 3, 5]
        expected_indices = [0, 2, 4]

        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        mock_factory = MagicMock()
        mock_service_factory_class.return_value = mock_factory

        mock_turn_service = MagicMock()
        mock_factory.create_session_turn_service.return_value = mock_turn_service

        # Execute
        result = delete_session_turns(session_id, turns)

        # Verify
        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, DeleteSessionTurnsResult)
        assert result.data.message is not None
        assert f"Successfully deleted turns {turns}" in result.data.message

        mock_turn_service.delete_turns.assert_called_once_with(
            session_id, expected_indices
        )
        mock_service_factory_class.assert_called_once()

    @patch("pipe.core.tools.delete_session_turns.ServiceFactory")
    @patch("pipe.core.tools.delete_session_turns.SettingsFactory.get_settings")
    def test_delete_session_turns_failure(
        self, mock_get_settings, mock_service_factory_class
    ):
        """Test failure during turn deletion."""
        # Setup
        session_id = "test-session"
        turns = [1]

        mock_get_settings.return_value = MagicMock()

        mock_factory = MagicMock()
        mock_service_factory_class.return_value = mock_factory

        mock_turn_service = MagicMock()
        mock_factory.create_session_turn_service.return_value = mock_turn_service
        mock_turn_service.delete_turns.side_effect = Exception("Database error")

        # Execute
        result = delete_session_turns(session_id, turns)

        # Verify
        assert isinstance(result, ToolResult)
        assert not result.is_success
        assert result.error is not None
        assert "Failed to delete turns" in result.error
        assert "Database error" in result.error

    @patch("pipe.core.tools.delete_session_turns.ServiceFactory")
    @patch("pipe.core.tools.delete_session_turns.SettingsFactory.get_settings")
    def test_delete_session_turns_empty_list(
        self, mock_get_settings, mock_service_factory_class
    ):
        """Test behavior with an empty list of turns."""
        # Setup
        session_id = "test-session"
        turns: list[int] = []

        mock_get_settings.return_value = MagicMock()
        mock_factory = MagicMock()
        mock_service_factory_class.return_value = mock_factory
        mock_turn_service = MagicMock()
        mock_factory.create_session_turn_service.return_value = mock_turn_service

        # Execute
        result = delete_session_turns(session_id, turns)

        # Verify
        assert result.is_success
        mock_turn_service.delete_turns.assert_called_once_with(session_id, [])
