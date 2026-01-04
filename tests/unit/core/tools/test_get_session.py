"""Unit tests for get_session tool."""

from unittest.mock import MagicMock, patch

from pipe.core.models.results.get_session_result import GetSessionResult
from pipe.core.tools.get_session import get_session

from tests.factories.models import SessionFactory, TurnFactory


class TestGetSession:
    """Tests for get_session function."""

    def test_get_session_missing_id(self) -> None:
        """Test get_session with missing session_id."""
        result = get_session(session_id=None)

        assert result.is_success is False
        assert result.error == "session_id is required."

    def test_get_session_not_found(self) -> None:
        """Test get_session when session is not found."""
        mock_service = MagicMock()
        mock_service.get_session.return_value = None

        result = get_session(session_id="non-existent", session_service=mock_service)

        assert result.is_success is False
        assert result.error == "Session non-existent not found."
        mock_service.get_session.assert_called_once_with("non-existent")

    def test_get_session_success(self) -> None:
        """Test get_session successfully retrieves and formats session data."""
        turns = [
            TurnFactory.create_user_task(instruction="Hello"),
            TurnFactory.create_model_response(content="Hi there!"),
        ]
        session = SessionFactory.create(session_id="test-session", turns=turns)

        mock_service = MagicMock()
        mock_service.get_session.return_value = session

        result = get_session(session_id="test-session", session_service=mock_service)

        assert result.is_success is True
        assert isinstance(result.data, GetSessionResult)
        assert result.data.session_id == "test-session"
        assert result.data.turns == ["User: Hello", "Assistant: Hi there!"]
        assert result.data.turns_count == 2

    def test_get_session_other_turn_types(self) -> None:
        """Test get_session with various turn types including fallback logic."""
        from unittest.mock import Mock

        # 1. Has content
        other_turn = Mock()
        other_turn.type = "function_call"
        other_turn.content = "call_func()"

        # 2. Has instruction (no content)
        other_turn_2 = Mock(spec=["type", "instruction"])
        other_turn_2.type = "system_log"
        other_turn_2.instruction = "Logged"

        # 3. Has neither (fallback to str)
        # Use a simple class to control str() behavior reliably
        class UnknownTurn:
            def __init__(self) -> None:
                self.type = "unknown"

            def __str__(self) -> str:
                return "UnknownTurnObject"

        other_turn_3 = UnknownTurn()

        session = SessionFactory.create(session_id="test-session")
        session.turns = [other_turn, other_turn_2, other_turn_3]

        mock_service = MagicMock()
        mock_service.get_session.return_value = session

        result = get_session(session_id="test-session", session_service=mock_service)

        assert result.is_success is True
        assert result.data is not None
        assert result.data.turns == [
            "function_call: call_func()",
            "system_log: Logged",
            "unknown: UnknownTurnObject",
        ]

    @patch("pipe.core.tools.get_session.os.getcwd")
    @patch("pipe.core.tools.get_session.SettingsFactory.get_settings")
    @patch("pipe.core.tools.get_session.ServiceFactory")
    def test_get_session_factory_creation(
        self, mock_service_factory_class, mock_get_settings, mock_getcwd
    ) -> None:
        """Test get_session when session_service is not provided (factory path)."""
        mock_getcwd.return_value = "/project/root"
        mock_settings = MagicMock()
        mock_get_settings.return_value = mock_settings

        mock_factory_instance = mock_service_factory_class.return_value
        mock_service = mock_factory_instance.create_session_service.return_value

        session = SessionFactory.create(session_id="test-session", turns=[])
        mock_service.get_session.return_value = session

        result = get_session(session_id="test-session", session_service=None)

        assert result.is_success is True
        assert result.data is not None
        assert result.data.session_id == "test-session"

        mock_getcwd.assert_called_once()
        mock_get_settings.assert_called_once()
        mock_service_factory_class.assert_called_once_with(
            "/project/root", mock_settings
        )
        mock_factory_instance.create_session_service.assert_called_once()
        mock_service.get_session.assert_called_once_with("test-session")

    @patch("pipe.core.tools.get_session.SettingsFactory.get_settings")
    def test_get_session_settings_failure(self, mock_get_settings) -> None:
        """Test get_session when settings loading fails."""
        mock_get_settings.side_effect = Exception("Config error")

        result = get_session(session_id="test-session", session_service=None)

        assert result.is_success is False
        assert "Failed to load settings: Config error" in result.error
