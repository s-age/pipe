"""Unit tests for BackupFiles collection."""

import json
import os
from unittest.mock import MagicMock

import pytest
from pipe.core.collections.backup_files import BackupFiles, SessionSummary
from pipe.core.repositories.session_repository import SessionRepository


class TestBackupFiles:
    """Tests for BackupFiles class."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock SessionRepository."""
        repository = MagicMock(spec=SessionRepository)
        repository.backups_dir = "/mock/backups"
        return repository

    @pytest.fixture
    def backup_files(self, mock_repository):
        """Create a BackupFiles instance with mock repository."""
        return BackupFiles(repository=mock_repository)

    def test_init(self, mock_repository):
        """Test initialization of BackupFiles."""
        backup_files = BackupFiles(repository=mock_repository)
        assert backup_files.repository == mock_repository

    def test_list_sessions_empty_dir(self, backup_files, mock_repository, tmp_path):
        """Test list_sessions when the backup directory is empty."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()
        mock_repository.backups_dir = str(backups_dir)

        sessions = backup_files.list_sessions()
        assert sessions == []

    def test_list_sessions_dir_not_exists(
        self, backup_files, mock_repository, tmp_path
    ):
        """Test list_sessions when the backup directory does not exist."""
        backups_dir = tmp_path / "non_existent"
        mock_repository.backups_dir = str(backups_dir)

        sessions = backup_files.list_sessions()
        assert sessions == []

    def test_list_sessions_valid_files(self, backup_files, mock_repository, tmp_path):
        """Test list_sessions with valid backup files."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()
        mock_repository.backups_dir = str(backups_dir)

        # Create a valid backup file
        # Format: {hash}-{datetime}.json
        # Example: hash-2025-12-04T075555.140300+0900.json
        filename = "abc-2025-12-04T075555.140300+0900.json"
        file_path = backups_dir / filename
        session_data = {
            "session_id": "test-session-1",
            "purpose": "Test purpose",
            "other": "data",
        }
        file_path.write_text(json.dumps(session_data), encoding="utf-8")

        sessions = backup_files.list_sessions()

        assert len(sessions) == 1
        summary = sessions[0]
        assert isinstance(summary, SessionSummary)
        assert summary.session_id == "test-session-1"
        assert summary.file_path == str(file_path)
        assert summary.purpose == "Test purpose"
        assert summary.deleted_at == "2025-12-04T07:55:55.140300+09:00"
        assert summary.session_data == session_data

    def test_list_sessions_mixed_files(self, backup_files, mock_repository, tmp_path):
        """Test list_sessions with a mix of valid and invalid files."""
        backups_dir = tmp_path / "backups"
        backups_dir.mkdir()
        mock_repository.backups_dir = str(backups_dir)

        # 1. Valid file
        f1 = backups_dir / "hash-2025-12-04T075555.140300+0900.json"
        f1.write_text(
            json.dumps({"session_id": "s1", "purpose": "p1"}), encoding="utf-8"
        )

        # 2. Valid file but no timestamp in name
        f2 = backups_dir / "no_timestamp.json"
        f2.write_text(
            json.dumps({"session_id": "s2", "purpose": "p2"}), encoding="utf-8"
        )

        # 3. Valid file but invalid timestamp format
        f3 = backups_dir / "hash-invalid_date.json"
        f3.write_text(
            json.dumps({"session_id": "s3", "purpose": "p3"}), encoding="utf-8"
        )

        # 4. Not a JSON file
        f4 = backups_dir / "not_json.txt"
        f4.write_text("not json", encoding="utf-8")

        # 5. Invalid JSON content
        f5 = backups_dir / "invalid_content.json"
        f5.write_text("{invalid json", encoding="utf-8")

        # 6. Missing session_id
        f6 = backups_dir / "missing_id.json"
        f6.write_text(json.dumps({"purpose": "p6"}), encoding="utf-8")

        sessions = backup_files.list_sessions()

        # Should only include s1, s2, s3
        assert len(sessions) == 3
        ids = {s.session_id for s in sessions}
        assert ids == {"s1", "s2", "s3"}

        # Check s1 (with timestamp)
        s1 = next(s for s in sessions if s.session_id == "s1")
        assert s1.deleted_at == "2025-12-04T07:55:55.140300+09:00"

        # Check s2 (no timestamp separator)
        s2 = next(s for s in sessions if s.session_id == "s2")
        assert s2.deleted_at is None

        # Check s3 (invalid timestamp format)
        s3 = next(s for s in sessions if s.session_id == "s3")
        assert s3.deleted_at is None

    def test_delete_success(self, backup_files, mock_repository):
        """Test deleting backups by session IDs."""
        session_ids = ["s1", "s2", "s3"]

        count = backup_files.delete(session_ids)

        assert count == 3
        assert mock_repository.delete_backup.call_count == 3
        mock_repository.delete_backup.assert_any_call("s1")
        mock_repository.delete_backup.assert_any_call("s2")
        mock_repository.delete_backup.assert_any_call("s3")

    def test_delete_partial_failure(self, backup_files, mock_repository):
        """Test delete continues even if some repository calls fail."""
        session_ids = ["s1", "fail", "s3"]

        def side_effect(sid):
            if sid == "fail":
                raise Exception("Delete failed")

        mock_repository.delete_backup.side_effect = side_effect

        count = backup_files.delete(session_ids)

        assert count == 2
        assert mock_repository.delete_backup.call_count == 3

    def test_delete_files_success(self, backup_files, tmp_path):
        """Test deleting specific backup files by path."""
        f1 = tmp_path / "f1.json"
        f2 = tmp_path / "f2.json"
        f1.write_text("data", encoding="utf-8")
        f2.write_text("data", encoding="utf-8")

        file_paths = [str(f1), str(f2)]
        count = backup_files.delete_files(file_paths)

        assert count == 2
        assert not f1.exists()
        assert not f2.exists()

    def test_delete_files_not_exists(self, backup_files, tmp_path):
        """Test delete_files handles non-existent files gracefully."""
        f1 = tmp_path / "exists.json"
        f1.write_text("data", encoding="utf-8")
        f2 = tmp_path / "not_exists.json"

        file_paths = [str(f1), str(f2)]
        count = backup_files.delete_files(file_paths)

        assert count == 1
        assert not f1.exists()

    def test_delete_files_permission_error(self, backup_files, tmp_path, monkeypatch):
        """Test delete_files continues even if os.remove fails."""
        f1 = tmp_path / "f1.json"
        f2 = tmp_path / "f2.json"
        f1.write_text("data", encoding="utf-8")
        f2.write_text("data", encoding="utf-8")

        original_remove = os.remove

        def mock_remove(path):
            if "f1.json" in str(path):
                raise PermissionError("Permission denied")
            original_remove(path)

        monkeypatch.setattr(os, "remove", mock_remove)

        file_paths = [str(f1), str(f2)]
        count = backup_files.delete_files(file_paths)

        assert count == 1
        assert f1.exists()
        assert not f2.exists()
