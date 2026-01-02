"""Unit tests for FilesToMove collection."""

from unittest.mock import MagicMock

import pytest
from pipe.core.collections.files_to_move import FilesToMove
from pipe.core.repositories.session_repository import SessionRepository


class TestFilesToMove:
    """Tests for FilesToMove collection."""

    @pytest.fixture
    def mock_repository(self) -> MagicMock:
        """Create a mock SessionRepository."""
        return MagicMock(spec=SessionRepository)

    def test_init(self, mock_repository: MagicMock) -> None:
        """Test initialization of FilesToMove."""
        session_ids = ["session-1", "session-2"]
        files_to_move = FilesToMove(session_ids=session_ids, repository=mock_repository)

        assert files_to_move.session_ids == session_ids
        assert files_to_move.repository == mock_repository

    def test_execute_all_success(self, mock_repository: MagicMock) -> None:
        """Test execute when all moves are successful."""
        session_ids = ["session-1", "session-2", "session-3"]
        mock_repository.move_to_backup.return_value = True

        files_to_move = FilesToMove(session_ids=session_ids, repository=mock_repository)
        result = files_to_move.execute()

        assert result == 3
        assert mock_repository.move_to_backup.call_count == 3
        for session_id in session_ids:
            mock_repository.move_to_backup.assert_any_call(session_id)

    def test_execute_partial_success(self, mock_repository: MagicMock) -> None:
        """Test execute when some moves fail."""
        session_ids = ["success-1", "fail-1", "success-2"]

        def side_effect(session_id: str) -> bool:
            return "success" in session_id

        mock_repository.move_to_backup.side_effect = side_effect

        files_to_move = FilesToMove(session_ids=session_ids, repository=mock_repository)
        result = files_to_move.execute()

        assert result == 2
        assert mock_repository.move_to_backup.call_count == 3

    def test_execute_empty_list(self, mock_repository: MagicMock) -> None:
        """Test execute with an empty list of session IDs."""
        files_to_move = FilesToMove(session_ids=[], repository=mock_repository)
        result = files_to_move.execute()

        assert result == 0
        assert mock_repository.move_to_backup.call_count == 0
