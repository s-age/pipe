"""Unit tests for get_sessions_final_turns tool."""

from unittest.mock import MagicMock, patch

from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.get_sessions_final_turns import get_sessions_final_turns


class TestGetSessionsFinalTurns:
    """Tests for get_sessions_final_turns function."""

    @patch("pipe.core.tools.get_sessions_final_turns.SessionRepository")
    @patch("pipe.core.tools.get_sessions_final_turns.SettingsFactory.get_settings")
    @patch("pipe.core.tools.get_sessions_final_turns.get_project_root")
    def test_empty_session_ids(
        self, mock_get_root, mock_get_settings, mock_repo_class
    ) -> None:
        """Test behavior when session_ids list is empty."""
        result = get_sessions_final_turns(session_ids=[])

        assert isinstance(result, ToolResult)
        assert result.data == {"sessions": []}
        assert result.error == "No session IDs provided"
        assert result.is_success is False

    @patch("pipe.core.tools.get_sessions_final_turns.SessionRepository")
    @patch("pipe.core.tools.get_sessions_final_turns.SettingsFactory.get_settings")
    @patch("pipe.core.tools.get_sessions_final_turns.get_project_root")
    def test_successful_retrieval(
        self, mock_get_root, mock_get_settings, mock_repo_class
    ) -> None:
        """Test successful retrieval of final turns from multiple sessions."""
        mock_get_root.return_value = "/mock/root"
        mock_repo = mock_repo_class.return_value

        # Mock session 1: has model_response
        turn1 = MagicMock()
        turn1.type = "user_task"
        turn2 = MagicMock()
        turn2.type = "model_response"
        turn2.content = "Response 1"
        turn2.timestamp = "2025-01-01T00:00:00Z"

        session1 = MagicMock()
        session1.turns = [turn1, turn2]

        # Mock session 2: has multiple model_responses, should get the last one
        turn3 = MagicMock()
        turn3.type = "model_response"
        turn3.content = "Response 2a"
        turn3.timestamp = "2025-01-01T00:01:00Z"
        turn4 = MagicMock()
        turn4.type = "model_response"
        turn4.content = "Response 2b"
        turn4.timestamp = "2025-01-01T00:02:00Z"

        session2 = MagicMock()
        session2.turns = [turn3, turn4]

        mock_repo.find.side_effect = lambda sid: {
            "abc123": session1,
            "def456": session2,
        }.get(sid)

        result = get_sessions_final_turns(session_ids=["abc123", "def456"])

        assert result.is_success is True
        sessions = result.data["sessions"]
        assert len(sessions) == 2

        assert sessions[0]["session_id"] == "abc123"
        assert sessions[0]["final_turn"] == {
            "type": "model_response",
            "content": "Response 1",
            "timestamp": "2025-01-01T00:00:00Z",
        }
        assert sessions[0]["error"] is None

        assert sessions[1]["session_id"] == "def456"
        assert sessions[1]["final_turn"] == {
            "type": "model_response",
            "content": "Response 2b",
            "timestamp": "2025-01-01T00:02:00Z",
        }
        assert sessions[1]["error"] is None

    @patch("pipe.core.tools.get_sessions_final_turns.SessionRepository")
    @patch("pipe.core.tools.get_sessions_final_turns.SettingsFactory.get_settings")
    @patch("pipe.core.tools.get_sessions_final_turns.get_project_root")
    def test_session_not_found(
        self, mock_get_root, mock_get_settings, mock_repo_class
    ) -> None:
        """Test behavior when a session is not found in the repository."""
        mock_repo = mock_repo_class.return_value
        mock_repo.find.return_value = None

        result = get_sessions_final_turns(session_ids=["missing"])

        assert result.is_success is True
        sessions = result.data["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "missing"
        assert sessions[0]["final_turn"] is None
        assert sessions[0]["error"] == "Session not found"

    @patch("pipe.core.tools.get_sessions_final_turns.SessionRepository")
    @patch("pipe.core.tools.get_sessions_final_turns.SettingsFactory.get_settings")
    @patch("pipe.core.tools.get_sessions_final_turns.get_project_root")
    def test_no_model_response_found(
        self, mock_get_root, mock_get_settings, mock_repo_class
    ) -> None:
        """Test behavior when a session exists but has no model_response turns."""
        mock_repo = mock_repo_class.return_value

        turn = MagicMock()
        turn.type = "user_task"
        session = MagicMock()
        session.turns = [turn]

        mock_repo.find.return_value = session

        result = get_sessions_final_turns(session_ids=["no_response"])

        assert result.is_success is True
        sessions = result.data["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "no_response"
        assert sessions[0]["final_turn"] is None
        assert sessions[0]["error"] == "No model_response turn found"

    @patch("pipe.core.tools.get_sessions_final_turns.SessionRepository")
    @patch("pipe.core.tools.get_sessions_final_turns.SettingsFactory.get_settings")
    @patch("pipe.core.tools.get_sessions_final_turns.get_project_root")
    def test_exception_during_processing(
        self, mock_get_root, mock_get_settings, mock_repo_class
    ) -> None:
        """Test behavior when an exception occurs during session processing."""
        mock_repo = mock_repo_class.return_value
        mock_repo.find.side_effect = Exception("Unexpected error")

        result = get_sessions_final_turns(session_ids=["error_session"])

        assert result.is_success is True
        sessions = result.data["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "error_session"
        assert sessions[0]["final_turn"] is None
        assert sessions[0]["error"] == "Unexpected error"

    @patch("pipe.core.tools.get_sessions_final_turns.SessionRepository")
    @patch("pipe.core.tools.get_sessions_final_turns.SettingsFactory.get_settings")
    @patch("pipe.core.tools.get_sessions_final_turns.get_project_root")
    def test_project_root_provided(
        self, mock_get_root, mock_get_settings, mock_repo_class
    ) -> None:
        """Test that get_project_root is not called if project_root is provided."""
        get_sessions_final_turns(session_ids=["test"], project_root="/provided/root")

        mock_get_root.assert_not_called()
        mock_repo_class.assert_called_once_with(
            "/provided/root", mock_get_settings.return_value
        )
