"""Unit tests for edit_session_turn tool."""

import os
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.results.edit_session_turn_result import EditSessionTurnResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.edit_session_turn import edit_session_turn


class TestEditSessionTurn:
    """Tests for edit_session_turn function."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings object."""
        settings = MagicMock()
        return settings

    @pytest.fixture
    def mock_repository(self):
        """Mock session repository."""
        repository = MagicMock()
        return repository

    @pytest.fixture
    def mock_turn_service(self, mock_repository):
        """Mock session turn service."""
        service = MagicMock()
        service.repository = mock_repository
        return service

    @pytest.fixture
    def mock_factory(self, mock_turn_service):
        """Mock service factory."""
        factory = MagicMock()
        factory.create_session_turn_service.return_value = mock_turn_service
        return factory

    @patch("pipe.core.tools.edit_session_turn.SettingsFactory.get_settings")
    @patch("pipe.core.tools.edit_session_turn.ServiceFactory")
    @patch("os.getcwd")
    def test_edit_user_task_turn_success(
        self,
        mock_getcwd,
        mock_service_factory_class,
        mock_get_settings,
        mock_factory,
        mock_turn_service,
        mock_repository,
        mock_settings,
    ):
        """Test successfully editing a user_task turn."""
        # Setup
        session_id = "test-session"
        turn_num = 1
        new_content = "Updated instruction"
        mock_getcwd.return_value = "/project/root"
        mock_get_settings.return_value = mock_settings
        mock_service_factory_class.return_value = mock_factory

        mock_session = MagicMock()
        mock_turn = MagicMock()
        mock_turn.type = "user_task"
        mock_session.turns = [mock_turn]
        mock_repository.find.return_value = mock_session

        # Execute
        result = edit_session_turn(
            turn=turn_num, new_content=new_content, session_id=session_id
        )

        # Verify
        assert isinstance(result, ToolResult)
        assert result.is_success
        assert isinstance(result.data, EditSessionTurnResult)
        assert f"Successfully edited turn {turn_num}" in result.data.message
        assert session_id in result.data.message

        mock_repository.find.assert_called_once_with(session_id)
        mock_repository.backup.assert_called_once_with(mock_session)
        mock_turn_service.edit_turn.assert_called_once_with(
            session_id, 0, {"instruction": new_content}
        )

    @patch("pipe.core.tools.edit_session_turn.SettingsFactory.get_settings")
    @patch("pipe.core.tools.edit_session_turn.ServiceFactory")
    @patch("os.getcwd")
    def test_edit_model_response_turn_success(
        self,
        mock_getcwd,
        mock_service_factory_class,
        mock_get_settings,
        mock_factory,
        mock_turn_service,
        mock_repository,
        mock_settings,
    ):
        """Test successfully editing a model_response turn."""
        # Setup
        session_id = "test-session"
        turn_num = 2
        new_content = "Updated content"
        mock_getcwd.return_value = "/project/root"
        mock_get_settings.return_value = mock_settings
        mock_service_factory_class.return_value = mock_factory

        mock_session = MagicMock()
        mock_turn1 = MagicMock()
        mock_turn2 = MagicMock()
        mock_turn2.type = "model_response"
        mock_session.turns = [mock_turn1, mock_turn2]
        mock_repository.find.return_value = mock_session

        # Execute
        result = edit_session_turn(
            turn=turn_num, new_content=new_content, session_id=session_id
        )

        # Verify
        assert result.is_success
        mock_turn_service.edit_turn.assert_called_once_with(
            session_id, 1, {"content": new_content}
        )

    def test_missing_session_id(self):
        """Test error when session_id is missing from args and env."""
        with patch.dict(os.environ, {}, clear=True):
            result = edit_session_turn(turn=1, new_content="test")

        assert not result.is_success
        assert "requires a session_id" in result.error

    def test_session_id_from_env(self):
        """Test resolving session_id from environment variable."""
        session_id = "env-session-id"
        with patch.dict(os.environ, {"PIPE_SESSION_ID": session_id}):
            # We mock the rest to avoid actual execution errors
            with patch(
                "pipe.core.tools.edit_session_turn.SettingsFactory.get_settings"
            ) as mock_get_settings:
                mock_get_settings.side_effect = Exception("Stop execution")
                result = edit_session_turn(turn=1, new_content="test")

        assert session_id in result.error

    def test_invalid_turn_number(self):
        """Test error when turn number is less than 1."""
        result = edit_session_turn(turn=0, new_content="test", session_id="test")
        assert not result.is_success
        assert "Turn number must be 1 or greater" in result.error

    @patch("pipe.core.tools.edit_session_turn.SettingsFactory.get_settings")
    @patch("pipe.core.tools.edit_session_turn.ServiceFactory")
    def test_session_not_found(
        self,
        mock_service_factory_class,
        mock_get_settings,
        mock_factory,
        mock_repository,
    ):
        """Test error when session is not found."""
        mock_get_settings.return_value = MagicMock()
        mock_service_factory_class.return_value = mock_factory
        mock_repository.find.return_value = None

        result = edit_session_turn(turn=1, new_content="test", session_id="missing")

        assert not result.is_success
        assert "Turn 1 not found in session missing" in result.error

    @patch("pipe.core.tools.edit_session_turn.SettingsFactory.get_settings")
    @patch("pipe.core.tools.edit_session_turn.ServiceFactory")
    def test_turn_index_out_of_range(
        self,
        mock_service_factory_class,
        mock_get_settings,
        mock_factory,
        mock_repository,
    ):
        """Test error when turn index is out of range."""
        mock_get_settings.return_value = MagicMock()
        mock_service_factory_class.return_value = mock_factory
        mock_session = MagicMock()
        mock_session.turns = []
        mock_repository.find.return_value = mock_session

        result = edit_session_turn(turn=1, new_content="test", session_id="test")

        assert not result.is_success
        assert "Turn 1 not found in session test" in result.error

    @patch("pipe.core.tools.edit_session_turn.SettingsFactory.get_settings")
    @patch("pipe.core.tools.edit_session_turn.ServiceFactory")
    def test_unsupported_turn_type(
        self,
        mock_service_factory_class,
        mock_get_settings,
        mock_factory,
        mock_repository,
    ):
        """Test error when turn type is not supported."""
        mock_get_settings.return_value = MagicMock()
        mock_service_factory_class.return_value = mock_factory
        mock_session = MagicMock()
        mock_turn = MagicMock()
        mock_turn.type = "unsupported"
        mock_session.turns = [mock_turn]
        mock_repository.find.return_value = mock_session

        result = edit_session_turn(turn=1, new_content="test", session_id="test")

        assert not result.is_success
        assert "Cannot edit turn of type unsupported" in result.error

    @patch("pipe.core.tools.edit_session_turn.SettingsFactory.get_settings")
    def test_exception_handling(self, mock_get_settings):
        """Test that exceptions are caught and returned as errors."""
        mock_get_settings.side_effect = Exception("Unexpected error")

        result = edit_session_turn(turn=1, new_content="test", session_id="test")

        assert not result.is_success
        assert "Failed to edit turn in session test: Unexpected error" in result.error
