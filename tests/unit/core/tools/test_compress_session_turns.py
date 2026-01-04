from unittest.mock import MagicMock, patch

from pipe.core.models.results.compress_session_turns_result import (
    CompressSessionTurnsResult,
)
from pipe.core.tools.compress_session_turns import compress_session_turns


class TestCompressSessionTurns:
    """Tests for compress_session_turns tool."""

    @patch("pipe.core.tools.compress_session_turns.os.getcwd")
    @patch("pipe.core.tools.compress_session_turns.SettingsFactory.get_settings")
    @patch("pipe.core.tools.compress_session_turns.ServiceFactory")
    def test_compress_success(self, MockServiceFactory, mock_get_settings, mock_getcwd):
        """Test successful compression of session turns."""
        # Setup mocks
        mock_getcwd.return_value = "/mock/project/root"
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        mock_factory_instance = MockServiceFactory.return_value
        mock_opt_service = MagicMock()
        mock_session_service = MagicMock()

        mock_factory_instance.create_session_optimization_service.return_value = (
            mock_opt_service
        )
        mock_factory_instance.create_session_service.return_value = mock_session_service

        mock_session = MagicMock()
        mock_session.turns = [MagicMock()] * 5  # 5 turns remaining
        mock_session_service.get_session.return_value = mock_session

        # Execute
        result = compress_session_turns(
            session_id="test-session",
            start_turn=1,
            end_turn=3,
            summary_text="Test summary",
        )

        # Assertions
        assert result.is_success
        assert isinstance(result.data, CompressSessionTurnsResult)
        assert result.data.current_turn_count == 5
        assert "Successfully compressed turns 1-3" in result.data.message

        mock_opt_service.replace_turn_range_with_summary.assert_called_once_with(
            "test-session", "Test summary", 0, 2
        )
        mock_session_service.get_session.assert_called_once_with("test-session")

    def test_validation_errors(self):
        """Test input validation for various invalid inputs."""
        # Missing session_id
        result = compress_session_turns("", 1, 2, "summary")
        assert not result.is_success
        assert "session_id is required" in result.error

        # Invalid start_turn
        result = compress_session_turns("sid", 0, 2, "summary")
        assert not result.is_success
        assert "start_turn must be a positive integer" in result.error

        # Invalid end_turn
        result = compress_session_turns("sid", 1, -1, "summary")
        assert not result.is_success
        assert "end_turn must be a positive integer" in result.error

        # start_turn > end_turn
        result = compress_session_turns("sid", 5, 2, "summary")
        assert not result.is_success
        assert "start_turn cannot be greater than end_turn" in result.error

        # Empty summary_text
        result = compress_session_turns("sid", 1, 2, "")
        assert not result.is_success
        assert "summary_text cannot be empty" in result.error

    @patch("pipe.core.tools.compress_session_turns.SettingsFactory.get_settings")
    def test_exception_handling(self, mock_get_settings):
        """Test that exceptions during execution are caught and returned as errors."""
        mock_get_settings.side_effect = Exception("Unexpected error")

        result = compress_session_turns("sid", 1, 2, "summary")

        assert not result.is_success
        assert "Failed to compress turns" in result.error
        assert "Unexpected error" in result.error

    @patch("pipe.core.tools.compress_session_turns.os.getcwd")
    @patch("pipe.core.tools.compress_session_turns.SettingsFactory.get_settings")
    @patch("pipe.core.tools.compress_session_turns.ServiceFactory")
    def test_session_not_found_after_compression(
        self, MockServiceFactory, mock_get_settings, mock_getcwd
    ):
        """Test behavior when session is not found after compression."""
        mock_getcwd.return_value = "/mock/root"
        mock_factory_instance = MockServiceFactory.return_value
        mock_session_service = MagicMock()
        mock_factory_instance.create_session_service.return_value = mock_session_service
        mock_session_service.get_session.return_value = None

        result = compress_session_turns("sid", 1, 2, "summary")

        assert result.is_success
        assert result.data.current_turn_count == 0
        assert "Session now has 0 turns" in result.data.message
