"""
Unit tests for FilesToDelete collection.
"""

from unittest.mock import MagicMock

import pytest
from pipe.core.collections.files_to_delete import FilesToDelete
from pipe.core.repositories.session_repository import SessionRepository


class TestFilesToDelete:
    """Tests for FilesToDelete class."""

    @pytest.fixture
    def mock_repository(self) -> MagicMock:
        """Create a mock SessionRepository."""
        return MagicMock(spec=SessionRepository)

    def test_init(self, mock_repository: MagicMock) -> None:
        """Test initialization of FilesToDelete."""
        session_ids = ["session-1", "session-2"]
        files_to_delete = FilesToDelete(session_ids, mock_repository)

        assert files_to_delete.session_ids == session_ids
        assert files_to_delete.repository == mock_repository

    def test_execute_all_success(self, mock_repository: MagicMock) -> None:
        """Test execute when all deletions are successful."""
        session_ids = ["session-1", "session-2", "session-3"]
        mock_repository.delete.return_value = True
        files_to_delete = FilesToDelete(session_ids, mock_repository)

        result = files_to_delete.execute()

        assert result == 3
        assert mock_repository.delete.call_count == 3
        for session_id in session_ids:
            mock_repository.delete.assert_any_call(session_id)

    def test_execute_partial_success(self, mock_repository: MagicMock) -> None:
        """Test execute when some deletions return False."""
        session_ids = ["session-1", "session-2"]
        # First succeeds, second fails
        mock_repository.delete.side_effect = [True, False]
        files_to_delete = FilesToDelete(session_ids, mock_repository)

        result = files_to_delete.execute()

        assert result == 1
        assert mock_repository.delete.call_count == 2

    def test_execute_with_exception(self, mock_repository: MagicMock) -> None:
        """Test execute when repository.delete raises an exception."""
        session_ids = ["session-1", "session-2", "session-3"]
        # First succeeds, second raises exception, third succeeds
        mock_repository.delete.side_effect = [True, Exception("Delete failed"), True]
        files_to_delete = FilesToDelete(session_ids, mock_repository)

        result = files_to_delete.execute()

        # Should continue after exception and count successful ones
        assert result == 2
        assert mock_repository.delete.call_count == 3

    def test_execute_empty_list(self, mock_repository: MagicMock) -> None:
        """Test execute with an empty list of session IDs."""
        files_to_delete = FilesToDelete([], mock_repository)

        result = files_to_delete.execute()

        assert result == 0
        assert mock_repository.delete.call_count == 0
