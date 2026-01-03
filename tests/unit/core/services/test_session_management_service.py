from unittest.mock import MagicMock, patch

import pytest
from pipe.core.collections.backup_files import SessionSummary
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_management_service import SessionManagementService


@pytest.fixture
def mock_repository():
    """Create a mock SessionRepository."""
    return MagicMock(spec=SessionRepository)


@pytest.fixture
def service(mock_repository):
    """Create a SessionManagementService instance with mocked repository."""
    return SessionManagementService(repository=mock_repository)


class TestSessionManagementService:
    """Tests for SessionManagementService."""

    def test_init(self, mock_repository):
        """Test initialization of SessionManagementService."""
        service = SessionManagementService(repository=mock_repository)
        assert service.repository == mock_repository

    @patch("pipe.core.services.session_management_service.FilesToDelete")
    def test_delete_sessions(self, MockFilesToDelete, service, mock_repository):
        """Test bulk deletion of sessions."""
        mock_instance = MockFilesToDelete.return_value
        mock_instance.execute.return_value = 2

        session_ids = ["session-1", "session-2"]
        result = service.delete_sessions(session_ids)

        assert result == 2
        MockFilesToDelete.assert_called_once_with(session_ids, mock_repository)
        mock_instance.execute.assert_called_once()

    @patch("pipe.core.services.session_management_service.FilesToMove")
    def test_move_sessions_to_backup(self, MockFilesToMove, service, mock_repository):
        """Test moving sessions to backup."""
        mock_instance = MockFilesToMove.return_value
        mock_instance.execute.return_value = 3

        session_ids = ["s1", "s2", "s3"]
        result = service.move_sessions_to_backup(session_ids)

        assert result == 3
        MockFilesToMove.assert_called_once_with(session_ids, mock_repository)
        mock_instance.execute.assert_called_once()

    @patch("pipe.core.services.session_management_service.BackupFiles")
    def test_list_backup_sessions(self, MockBackupFiles, service, mock_repository):
        """Test listing backup sessions."""
        mock_instance = MockBackupFiles.return_value
        expected_sessions = [
            SessionSummary(
                session_id="s1",
                file_path="path/s1.json",
                purpose="p1",
                deleted_at=None,
                session_data={},
            ),
            SessionSummary(
                session_id="s2",
                file_path="path/s2.json",
                purpose="p2",
                deleted_at=None,
                session_data={},
            ),
        ]
        mock_instance.list_sessions.return_value = expected_sessions

        result = service.list_backup_sessions()

        assert result == expected_sessions
        MockBackupFiles.assert_called_once_with(mock_repository)
        mock_instance.list_sessions.assert_called_once()

    @patch("pipe.core.services.session_management_service.BackupFiles")
    def test_delete_backup_sessions(self, MockBackupFiles, service, mock_repository):
        """Test bulk deletion of backup sessions."""
        mock_instance = MockBackupFiles.return_value
        mock_instance.delete.return_value = 1

        session_ids = ["s1"]
        result = service.delete_backup_sessions(session_ids)

        assert result == 1
        MockBackupFiles.assert_called_once_with(mock_repository)
        mock_instance.delete.assert_called_once_with(session_ids)

    @patch("pipe.core.services.session_management_service.BackupFiles")
    def test_delete_backups_by_session_ids(
        self, MockBackupFiles, service, mock_repository
    ):
        """Test deleting backup sessions by their session IDs."""
        mock_instance = MockBackupFiles.return_value
        backup_sessions = [
            SessionSummary(
                session_id="s1",
                file_path="path/s1.json",
                purpose=None,
                deleted_at=None,
                session_data={},
            ),
            SessionSummary(
                session_id="s2",
                file_path="path/s2.json",
                purpose=None,
                deleted_at=None,
                session_data={},
            ),
            SessionSummary(
                session_id="s3",
                file_path="path/s3.json",
                purpose=None,
                deleted_at=None,
                session_data={},
            ),
        ]
        mock_instance.list_sessions.return_value = backup_sessions
        mock_instance.delete_files.return_value = 2

        session_ids = ["s1", "s3", "s4"]  # s4 is not in backup
        result = service.delete_backups_by_session_ids(session_ids)

        assert result == 2
        MockBackupFiles.assert_called_once_with(mock_repository)
        mock_instance.list_sessions.assert_called_once()
        mock_instance.delete_files.assert_called_once_with(
            ["path/s1.json", "path/s3.json"]
        )

    @patch("pipe.core.services.session_management_service.BackupFiles")
    def test_delete_backups_by_session_ids_empty(
        self, MockBackupFiles, service, mock_repository
    ):
        """Test deleting backup sessions with empty session IDs list."""
        mock_instance = MockBackupFiles.return_value
        mock_instance.list_sessions.return_value = []
        mock_instance.delete_files.return_value = 0

        result = service.delete_backups_by_session_ids([])

        assert result == 0
        mock_instance.delete_files.assert_called_once_with([])

    @patch("pipe.core.services.session_management_service.BackupFiles")
    def test_delete_backup_files(self, MockBackupFiles, service, mock_repository):
        """Test deleting specific backup files."""
        mock_instance = MockBackupFiles.return_value
        mock_instance.delete_files.return_value = 5

        file_paths = ["p1", "p2", "p3", "p4", "p5"]
        result = service.delete_backup_files(file_paths)

        assert result == 5
        MockBackupFiles.assert_called_once_with(mock_repository)
        mock_instance.delete_files.assert_called_once_with(file_paths)
