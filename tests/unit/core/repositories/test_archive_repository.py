"""
Unit tests for ArchiveRepository.
"""

import json
import os
import threading
from unittest.mock import patch

import pytest
from pipe.core.repositories.archive_repository import ArchiveRepository

from tests.factories.models import SessionFactory


@pytest.fixture
def repository(tmp_path):
    """Create an ArchiveRepository instance with a temporary directory."""
    backups_dir = tmp_path / "backups"
    return ArchiveRepository(backups_dir=str(backups_dir))


class TestArchiveRepositoryInitialization:
    """Test ArchiveRepository initialization."""

    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates the backups directory."""
        backups_dir = tmp_path / "backups"
        assert not backups_dir.exists()

        ArchiveRepository(backups_dir=str(backups_dir))

        assert backups_dir.exists()


class TestArchiveRepositoryBackupMethods:
    """
    Test the direct backup methods (save_backup, list_backups, etc.).
    These methods use the format: {session_id}_{timestamp}.json
    """

    def test_save_backup(self, repository):
        """Test saving a backup with specific timestamp."""
        session = SessionFactory.create(session_id="test-123")
        timestamp = "2025-01-01T12:00:00+00:00"

        path = repository.save_backup("test-123", session, timestamp)

        assert os.path.exists(path)
        assert "test-123_2025-01-01T12:00:00+00:00.json" in path

        # Verify content
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["session_id"] == "test-123"

    def test_save_backup_sanitizes_filename(self, repository):
        """Test that session IDs with slashes are sanitized."""
        session = SessionFactory.create(session_id="folder/test-123")
        timestamp = "2025-01-01T12:00:00+00:00"

        path = repository.save_backup("folder/test-123", session, timestamp)

        assert os.path.exists(path)
        assert "folder__test-123" in os.path.basename(path)

    def test_list_backups(self, repository):
        """Test listing backups for a session."""
        session = SessionFactory.create(session_id="test-123")
        ts1 = "2025-01-01T10:00:00+00:00"
        ts2 = "2025-01-01T12:00:00+00:00"

        repository.save_backup("test-123", session, ts1)
        repository.save_backup("test-123", session, ts2)
        # Another session
        repository.save_backup("other-456", session, ts1)

        backups = repository.list_backups("test-123")

        assert len(backups) == 2
        # Should be sorted descending (newest first)
        assert ts2 in backups[0][0]
        assert ts1 in backups[1][0]

    def test_restore_backup(self, repository):
        """Test restoring a session from a backup file."""
        original_session = SessionFactory.create(
            session_id="test-123", purpose="Original Purpose"
        )
        timestamp = "2025-01-01T12:00:00+00:00"

        path = repository.save_backup("test-123", original_session, timestamp)

        restored_session = repository.restore_backup(path)

        assert restored_session.session_id == original_session.session_id
        assert restored_session.purpose == original_session.purpose

    def test_delete_backup(self, repository):
        """Test deleting a specific backup file."""
        session = SessionFactory.create(session_id="test-123")
        timestamp = "2025-01-01T12:00:00+00:00"

        path = repository.save_backup("test-123", session, timestamp)
        assert os.path.exists(path)

        result = repository.delete_backup(path)

        assert result is True
        assert not os.path.exists(path)

    def test_delete_nonexistent_backup(self, repository):
        """Test deleting a non-existent backup returns False."""
        result = repository.delete_backup("/path/to/nonexistent.json")
        assert result is False

    def test_delete_all_backups(self, repository):
        """Test deleting all backups for a session."""
        session = SessionFactory.create(session_id="test-123")
        repository.save_backup("test-123", session, "ts1")
        repository.save_backup("test-123", session, "ts2")
        repository.save_backup("other-456", session, "ts1")

        count = repository.delete_all_backups("test-123")

        assert count == 2
        assert len(repository.list_backups("test-123")) == 0
        assert len(repository.list_backups("other-456")) == 1


class TestArchiveRepositoryHashMethods:
    """
    Test the hashed backup methods (save, restore, list, delete).
    These methods use the format: {hash}-{timestamp}.json
    """

    def test_save_creates_hashed_file(self, repository):
        """Test saving a session creates a hashed filename."""
        session = SessionFactory.create(session_id="test-hash-123")

        path = repository.save(session)

        assert os.path.exists(path)
        # Filename should contain sha256 of session_id
        # sha256("test-hash-123")
        # = 5f7f...
        filename = os.path.basename(path)
        assert filename.endswith(".json")
        assert "-" in filename  # hash-timestamp separator

        # Verify content
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["session_id"] == "test-hash-123"

    def test_restore_finds_latest_backup(self, repository):
        """Test restore returns the latest backup for a session."""
        session = SessionFactory.create(session_id="test-restore", purpose="Initial")

        # Save first version
        with patch(
            "pipe.core.repositories.archive_repository.get_current_timestamp"
        ) as mock_time:
            # Format used by repository (internally strips colons)
            mock_time.return_value = "2025-01-01T10:00:00+00:00"
            repository.save(session)

        # Save second version
        session.purpose = "Updated"
        with patch(
            "pipe.core.repositories.archive_repository.get_current_timestamp"
        ) as mock_time:
            mock_time.return_value = "2025-01-01T12:00:00+00:00"
            repository.save(session)

        restored = repository.restore("test-restore")

        assert restored is not None
        assert restored.session_id == "test-restore"
        assert restored.purpose == "Updated"

    def test_restore_returns_none_if_no_backup(self, repository):
        """Test restore returns None if no backup exists."""
        result = repository.restore("nonexistent")
        assert result is None

    def test_list_summaries(self, repository):
        """Test listing all backed up sessions as summaries."""
        session1 = SessionFactory.create(session_id="s1", purpose="P1")
        session2 = SessionFactory.create(session_id="s2", purpose="P2")

        # Mock timestamps to control filename generation for sorting
        with patch(
            "pipe.core.repositories.archive_repository.get_current_timestamp"
        ) as mock_time:
            # S1: 10:00 -> filename will include 100000
            mock_time.return_value = "2025-01-01T10:00:00.000000+00:00"
            repository.save(session1)

        with patch(
            "pipe.core.repositories.archive_repository.get_current_timestamp"
        ) as mock_time:
            # S2: 12:00 -> filename will include 120000
            mock_time.return_value = "2025-01-01T12:00:00.000000+00:00"
            repository.save(session2)

        summaries = repository.list()

        assert len(summaries) == 2
        # Should be sorted by deleted_at (derived from timestamp in filename) descending
        assert summaries[0].session_id == "s2"
        assert summaries[1].session_id == "s1"
        assert summaries[0].purpose == "P2"
        assert summaries[1].purpose == "P1"

    def test_list_skips_corrupted_files(self, repository):
        """Test that list() skips invalid JSON files."""
        # Create a valid backup
        session = SessionFactory.create(session_id="valid")
        repository.save(session)

        # Create a corrupted file
        corrupted_path = os.path.join(repository.backups_dir, "corrupted.json")
        with open(corrupted_path, "w") as f:
            f.write("{ invalid json")

        summaries = repository.list()

        # Should only find the valid one
        assert len(summaries) == 1
        assert summaries[0].session_id == "valid"

    def test_delete_removes_all_versions(self, repository):
        """Test delete removes all backup versions for a session."""
        session = SessionFactory.create(session_id="test-del")

        repository.save(session)
        repository.save(session)

        assert len(os.listdir(repository.backups_dir)) >= 2  # + locks

        deleted = repository.delete("test-del")

        assert deleted is True
        # Check that no json files for this session remain
        # Note: We rely on implementation detail that filenames start with hash
        import hashlib

        session_hash = hashlib.sha256(b"test-del").hexdigest()

        remaining = [
            f
            for f in os.listdir(repository.backups_dir)
            if f.startswith(session_hash) and f.endswith(".json")
        ]
        assert len(remaining) == 0


class TestArchiveRepositoryConcurrency:
    """Test file locking for concurrent operations."""

    def test_save_concurrently(self, repository):
        """Test concurrent saves are handled safely."""
        session = SessionFactory.create(session_id="concurrent")

        def save_session():
            repository.save(session)

        threads = [threading.Thread(target=save_session) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should be able to restore
        restored = repository.restore("concurrent")
        assert restored is not None
        assert restored.session_id == "concurrent"


class TestArchiveRepositoryErrorHandling:
    """Test error handling in ArchiveRepository."""

    def test_restore_backup_file_not_found(self, repository):
        """Test restore_backup raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            repository.restore_backup("/nonexistent/path.json")

    def test_restore_backup_invalid_json(self, repository, tmp_path):
        """Test restore_backup raises error on invalid JSON."""
        p = tmp_path / "invalid.json"
        p.write_text("{ invalid", encoding="utf-8")

        with pytest.raises(Exception):  # JSONDecodeError or ValueError
            repository.restore_backup(str(p))

    def test_timestamp_format_consistency(self, repository):
        """
        Verify that the timestamp format produced by save()
        is compatible with _extract_deleted_at().
        """
        session = SessionFactory.create(session_id="ts-test")

        # Use a fixed time
        fixed_dt = "2025-12-14T10:30:45.123456+09:00"

        with patch(
            "pipe.core.repositories.archive_repository.get_current_timestamp",
            return_value=fixed_dt,
        ):
            path = repository.save(session)

        filename = os.path.basename(path)

        # Check if list() can parse it
        summaries = repository.list()
        summary = next(s for s in summaries if s.session_id == "ts-test")

        if summary.deleted_at is None:
            pytest.fail(
                f"Could not extract timestamp from filename: {filename}. "
                "Check save() vs _extract_deleted_at() formats."
            )

        assert "2025" in summary.deleted_at
