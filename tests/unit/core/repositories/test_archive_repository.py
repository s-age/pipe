import hashlib
import json
import os
import zoneinfo
from datetime import datetime
from unittest.mock import patch

import pytest
from pipe.core.models.session import Session
from pipe.core.repositories.archive_repository import ArchiveRepository, SessionSummary


@pytest.fixture
def mock_timezone_obj():
    """Create a mock timezone object for consistent timestamp generation."""
    return zoneinfo.ZoneInfo("Asia/Tokyo")


@pytest.fixture
def archive_repository(tmp_path, mock_timezone_obj):
    """Create an ArchiveRepository instance with a temporary directory."""
    backups_dir = tmp_path / "backups"
    return ArchiveRepository(
        backups_dir=str(backups_dir), timezone_obj=mock_timezone_obj
    )


@pytest.fixture
def sample_session():
    """Create a sample Session object for testing."""
    return Session(
        session_id="test-session-123",
        created_at="2025-01-01T00:00:00+09:00",
        purpose="Test purpose",
        background="Test background",
        roles=["Developer", "Tester"],
        multi_step_reasoning_enabled=True,
    )


class TestSessionSummary:
    """Test SessionSummary class."""

    def test_init(self):
        """Test that SessionSummary initializes correctly."""
        summary = SessionSummary(
            session_id="test-123",
            file_path="/path/to/file.json",
            purpose="A test purpose",
            deleted_at="2025-01-01T00:00:00+09:00",
        )
        assert summary.session_id == "test-123"
        assert summary.file_path == "/path/to/file.json"
        assert summary.purpose == "A test purpose"
        assert summary.deleted_at == "2025-01-01T00:00:00+09:00"


class TestArchiveRepositoryInit:
    """Test ArchiveRepository.__init__ method."""

    def test_init_creates_backups_dir(self, tmp_path):
        """Test that the backups directory is created if it doesn't exist."""
        backups_dir = tmp_path / "new_backups"
        assert not os.path.exists(backups_dir)
        ArchiveRepository(backups_dir=str(backups_dir))
        assert os.path.exists(backups_dir)
        assert os.path.isdir(backups_dir)

    def test_init_uses_default_timezone_if_none(self, tmp_path):
        """Test that UTC is used as default timezone if none is provided."""
        repo = ArchiveRepository(backups_dir=str(tmp_path / "backups"))
        assert repo.timezone_obj.key == "UTC"

    def test_init_uses_provided_timezone(self, tmp_path):
        """Test that the provided timezone is used."""
        tokyo_tz = zoneinfo.ZoneInfo("Asia/Tokyo")
        repo = ArchiveRepository(
            backups_dir=str(tmp_path / "backups"), timezone_obj=tokyo_tz
        )
        assert repo.timezone_obj.key == "Asia/Tokyo"


class TestArchiveRepositorySaveBackup:
    """Test ArchiveRepository.save_backup() method."""

    def test_save_backup_creates_file(self, archive_repository, sample_session):
        """Test that save_backup creates a backup file."""
        timestamp = "2025-01-01T00:00:00.000000+09:00"  # Added microseconds
        backup_path = archive_repository.save_backup(
            sample_session.session_id, sample_session, timestamp
        )

        session_hash = hashlib.sha256(
            sample_session.session_id.encode("utf-8")
        ).hexdigest()
        safe_timestamp = timestamp.replace(":", "")
        expected_filename_part = f"{session_hash}-{safe_timestamp}.json"
        assert expected_filename_part in backup_path
        assert os.path.exists(backup_path)
        assert os.path.isfile(backup_path)
        assert backup_path.startswith(str(archive_repository.backups_dir))

    def test_save_backup_content_integrity(self, archive_repository, sample_session):
        """Test that the saved backup content matches the original session."""
        timestamp = "2025-01-01T00:00:00.000000+09:00"  # Added microseconds
        backup_path = archive_repository.save_backup(
            sample_session.session_id, sample_session, timestamp
        )

        with open(backup_path, encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == sample_session.model_dump(mode="json")

    def test_save_backup_with_slashed_session_id(
        self, archive_repository, sample_session
    ):
        """Test saving a backup with a session ID containing slashes."""
        session_id_with_slash = "parent/child/test-session"
        sample_session.session_id = session_id_with_slash
        timestamp = "2025-01-01T00:00:00.000000+09:00"  # Added microseconds
        backup_path = archive_repository.save_backup(
            session_id_with_slash, sample_session, timestamp
        )

        session_hash = hashlib.sha256(session_id_with_slash.encode("utf-8")).hexdigest()
        safe_timestamp = timestamp.replace(":", "")
        expected_filename_part = f"{session_hash}-{safe_timestamp}.json"
        assert expected_filename_part in backup_path
        assert os.path.exists(backup_path)
        # The original test checked for "__" in basename, but the current
        # implementation uses hash.
        # assert "__" in os.path.basename(backup_path)
        # This assertion is no longer valid


class TestArchiveRepositoryListBackups:
    """Test ArchiveRepository.list_backups() method."""

    def test_list_backups_for_existing_session(
        self, archive_repository, sample_session
    ):
        """Test listing backups for an existing session."""
        timestamps = [
            "2025-01-01T00:00:00.000000+09:00",
            "2025-01-02T00:00:00.000000+09:00",
        ]  # Added microseconds
        for ts in timestamps:
            archive_repository.save_backup(
                sample_session.session_id, sample_session, ts
            )

        backups = archive_repository.list_backups(sample_session.session_id)
        assert len(backups) == 2
        # Check sorting (most recent first)
        assert timestamps[1].replace(":", "") in backups[0][0]
        assert timestamps[0].replace(":", "") in backups[1][0]

    def test_list_backups_for_nonexistent_session(self, archive_repository):
        """Test listing backups for a non-existent session."""
        backups = archive_repository.list_backups("nonexistent-session")
        assert len(backups) == 0

    def test_list_backups_with_no_backups_at_all(self, archive_repository):
        """Test listing backups when no backups exist in the directory."""
        backups = archive_repository.list_backups("any-session-id")
        assert len(backups) == 0

    def test_list_backups_with_other_session_backups(
        self, archive_repository, sample_session
    ):
        """Test that list_backups only returns backups for the specified session."""
        archive_repository.save_backup(
            sample_session.session_id,
            sample_session,
            "2025-01-01T00:00:00.000000+09:00",  # Added microseconds
        )
        other_session = sample_session.model_copy(
            update={"session_id": "other-session"}
        )
        archive_repository.save_backup(
            other_session.session_id,
            other_session,
            "2025-01-01T00:00:00.000000+09:00",  # Added microseconds
        )

        backups = archive_repository.list_backups(sample_session.session_id)
        assert len(backups) == 1
        session_hash = hashlib.sha256(
            sample_session.session_id.encode("utf-8")
        ).hexdigest()
        assert session_hash in backups[0][0]
        other_session_hash = hashlib.sha256(
            other_session.session_id.encode("utf-8")
        ).hexdigest()
        assert other_session_hash not in backups[0][0]


class TestArchiveRepositoryRestoreBackup:
    """Test ArchiveRepository.restore_backup() method."""

    def test_restore_existing_backup(self, archive_repository, sample_session):
        """Test restoring an existing backup file."""
        timestamp = "2025-01-01T00:00:00.000000+09:00"  # Added microseconds
        backup_path = archive_repository.save_backup(
            sample_session.session_id, sample_session, timestamp
        )

        restored_session = archive_repository.restore_backup(backup_path)
        assert restored_session.session_id == sample_session.session_id
        assert restored_session.purpose == sample_session.purpose
        assert restored_session.model_dump(mode="json") == sample_session.model_dump(
            mode="json"
        )

    def test_restore_nonexistent_backup_raises_filenotfounderror(
        self, archive_repository, tmp_path
    ):
        """Test that restoring a non-existent backup raises FileNotFoundError."""
        non_existent_path = tmp_path / "nonexistent.json"
        with pytest.raises(
            FileNotFoundError, match=f"Backup file not found: {non_existent_path}"
        ):
            archive_repository.restore_backup(str(non_existent_path))

    def test_restore_corrupted_json_raises_valueerror(
        self, archive_repository, tmp_path
    ):
        """Test that restoring a corrupted JSON file raises ValueError."""
        corrupted_path = tmp_path / "backups" / "corrupted.json"
        os.makedirs(os.path.dirname(corrupted_path), exist_ok=True)
        with open(corrupted_path, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        with pytest.raises(
            ValueError, match=f"Invalid JSON data in backup file: {corrupted_path}"
        ):
            archive_repository.restore_backup(str(corrupted_path))

    def test_restore_invalid_session_data_raises_validation_error(
        self, archive_repository, tmp_path
    ):
        """Test that restoring a JSON file with invalid Session data raises Pydantic
        ValidationError."""
        invalid_data_path = tmp_path / "backups" / "invalid_session.json"
        os.makedirs(os.path.dirname(invalid_data_path), exist_ok=True)
        with open(invalid_data_path, "w", encoding="utf-8") as f:
            json.dump({"not_a_session_field": "value"}, f)

        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            archive_repository.restore_backup(str(invalid_data_path))


class TestArchiveRepositoryDeleteBackup:
    """Test ArchiveRepository.delete_backup() method."""

    def test_delete_existing_backup(self, archive_repository, sample_session):
        """Test deleting an existing backup file."""
        timestamp = "2025-01-01T00:00:00.000000+09:00"  # Added microseconds
        backup_path = archive_repository.save_backup(
            sample_session.session_id, sample_session, timestamp
        )
        assert os.path.exists(backup_path)

        result = archive_repository.delete_backup(backup_path)
        assert result is True
        assert not os.path.exists(backup_path)

    def test_delete_nonexistent_backup(self, archive_repository, tmp_path):
        """Test deleting a non-existent backup file returns False."""
        non_existent_path = tmp_path / "nonexistent.json"
        result = archive_repository.delete_backup(str(non_existent_path))
        assert result is False


class TestArchiveRepositoryDeleteAllBackups:
    """Test ArchiveRepository.delete_all_backups() method."""

    def test_delete_all_backups_for_existing_session(
        self, archive_repository, sample_session
    ):
        """Test deleting all backups for an existing session."""
        timestamps = [
            "2025-01-01T00:00:00.000000+09:00",
            "2025-01-02T00:00:00.000000+09:00",
        ]  # Added microseconds
        for ts in timestamps:
            archive_repository.save_backup(
                sample_session.session_id, sample_session, ts
            )

        # Add a backup for another session to ensure it's not deleted
        other_session = sample_session.model_copy(
            update={"session_id": "other-session"}
        )
        archive_repository.save_backup(
            other_session.session_id,
            other_session,
            "2025-01-01T00:00:00.000000+09:00",  # Added microseconds
        )

        deleted_count = archive_repository.delete_all_backups(sample_session.session_id)
        assert deleted_count == 2
        assert len(archive_repository.list_backups(sample_session.session_id)) == 0
        assert (
            len(archive_repository.list_backups(other_session.session_id)) == 1
        )  # Other session backup should remain

    def test_delete_all_backups_for_nonexistent_session(self, archive_repository):
        """Test deleting all backups for a non-existent session returns 0."""
        deleted_count = archive_repository.delete_all_backups("nonexistent-session")
        assert deleted_count == 0

    def test_delete_all_backups_with_no_backups_at_all(self, archive_repository):
        """Test deleting all backups when no backups exist in the directory."""
        deleted_count = archive_repository.delete_all_backups("any-session-id")
        assert deleted_count == 0


class TestArchiveRepositoryList:
    """Test ArchiveRepository.list() method."""

    def test_list_no_backups(self, archive_repository):
        """Test listing when no backups exist."""
        summaries = archive_repository.list()
        assert len(summaries) == 0

    def test_list_single_backup(self, archive_repository, sample_session):
        """Test listing a single backup."""
        timestamp = "2025-01-01T00:00:00.000000+09:00"  # Added microseconds
        backup_path = archive_repository.save_backup(
            sample_session.session_id, sample_session, timestamp
        )

        summaries = archive_repository.list()
        assert len(summaries) == 1
        summary = summaries[0]
        assert summary.session_id == sample_session.session_id
        assert summary.file_path == backup_path
        assert summary.purpose == sample_session.purpose
        assert (
            summary.deleted_at
            == datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z").isoformat()
        )

    def test_list_multiple_backups_sorted_by_deleted_at(
        self, archive_repository, sample_session
    ):
        """Test listing multiple backups and ensure they are sorted by deleted_at."""
        session_id_1 = "session-A"
        session_id_2 = "session-B"

        # Save backups with different timestamps
        session_A_old = sample_session.model_copy(
            update={"session_id": session_id_1, "purpose": "Purpose A Old"}
        )
        archive_repository.save_backup(
            session_id_1,
            session_A_old,
            "2025-01-01T10:00:00.000000+09:00",  # Added microseconds
        )

        session_B_new = sample_session.model_copy(
            update={"session_id": session_id_2, "purpose": "Purpose B New"}
        )
        archive_repository.save_backup(
            session_id_2,
            session_B_new,
            "2025-01-02T11:00:00.000000+09:00",  # Added microseconds
        )

        session_A_new = sample_session.model_copy(
            update={"session_id": session_id_1, "purpose": "Purpose A New"}
        )
        archive_repository.save_backup(
            session_id_1,
            session_A_new,
            "2025-01-03T12:00:00.000000+09:00",  # Added microseconds
        )

        summaries = archive_repository.list()
        assert len(summaries) == 3

        # Expect sorting by deleted_at descending (most recent first)
        assert summaries[0].session_id == session_id_1
        assert summaries[0].purpose == "Purpose A New"
        assert (
            summaries[0].deleted_at
            == datetime.strptime(
                "2025-01-03T12:00:00.000000+09:00", "%Y-%m-%dT%H:%M:%S.%f%z"
            ).isoformat()
        )

        assert summaries[1].session_id == session_id_2
        assert summaries[1].purpose == "Purpose B New"
        assert (
            summaries[1].deleted_at
            == datetime.strptime(
                "2025-01-02T11:00:00.000000+09:00", "%Y-%m-%dT%H:%M:%S.%f%z"
            ).isoformat()
        )

        assert summaries[2].session_id == session_id_1
        assert summaries[2].purpose == "Purpose A Old"
        assert (
            summaries[2].deleted_at
            == datetime.strptime(
                "2025-01-01T10:00:00.000000+09:00", "%Y-%m-%dT%H:%M:%S.%f%z"
            ).isoformat()
        )

    def test_list_skips_corrupted_files(
        self, archive_repository, tmp_path, sample_session
    ):
        """Test that list() skips corrupted JSON files."""
        # Create a valid backup
        archive_repository.save_backup(
            sample_session.session_id,
            sample_session,
            "2025-01-01T00:00:00.000000+09:00",  # Added microseconds
        )

        # Create a corrupted file
        corrupted_path = tmp_path / "backups" / "corrupted.json"
        with open(corrupted_path, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        # Create a file with missing session_id
        missing_id_path = (
            tmp_path / "backups" / "missing_id_2025-01-02T000000.000000+0900.json"
        )  # Added microseconds
        with open(missing_id_path, "w", encoding="utf-8") as f:
            json.dump({"purpose": "no id"}, f)

        summaries = archive_repository.list()
        assert len(summaries) == 1  # Only the valid backup should be listed
        assert summaries[0].session_id == sample_session.session_id


class TestArchiveRepositorySave:
    """Test ArchiveRepository.save() method (using SHA256 hash and file_lock)."""

    @patch("pipe.core.repositories.archive_repository.get_current_timestamp")
    def test_save_creates_file_with_hash_and_timestamp(
        self, mock_get_current_timestamp, archive_repository, sample_session
    ):
        """Test that save creates a backup file with SHA256 hash and timestamp."""
        mock_timestamp = datetime(
            2025, 1, 1, 10, 30, 45, 123456, tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo")
        )
        mock_get_current_timestamp.return_value = mock_timestamp.isoformat()

        backup_path = archive_repository.save(sample_session)

        session_hash = hashlib.sha256(
            sample_session.session_id.encode("utf-8")
        ).hexdigest()
        expected_filename_part = (
            f"{session_hash}-{mock_timestamp.isoformat().replace(':', '')}.json"
        )
        assert expected_filename_part in backup_path
        assert os.path.exists(backup_path)

    def test_save_content_integrity(self, archive_repository, sample_session):
        """Test that the saved content matches the original session."""
        backup_path = archive_repository.save(sample_session)

        with open(backup_path, encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == sample_session.model_dump(mode="json")

    def test_save_uses_file_lock(self, archive_repository, sample_session):
        """Test that save uses file locking."""
        with patch(
            "pipe.core.repositories.archive_repository.file_lock"
        ) as mock_file_lock:  # Changed patch target
            archive_repository.save(sample_session)
            mock_file_lock.assert_called_once()


class TestArchiveRepositoryRestore:
    """Test ArchiveRepository.restore() method (using SHA256 hash and file_lock)."""

    def test_restore_latest_backup_for_existing_session(
        self, archive_repository, sample_session
    ):
        """Test restoring the latest backup for an existing session."""
        # Save an older backup
        old_timestamp = "2025-01-01T00:00:00.000000+09:00"  # Added microseconds
        archive_repository.save_backup(
            sample_session.session_id, sample_session, old_timestamp
        )

        # Save a newer backup (this is what `save` method would do)
        newer_session = sample_session.model_copy(update={"purpose": "Newer purpose"})
        with patch(
            "pipe.core.utils.datetime.get_current_timestamp"
        ) as mock_get_current_timestamp:
            mock_get_current_timestamp.return_value = datetime(
                2025,
                1,
                2,
                0,
                0,
                0,
                000000,
                tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo"),  # Added microseconds
            )
            archive_repository.save(newer_session)

        restored_session = archive_repository.restore(sample_session.session_id)
        assert restored_session is not None
        assert restored_session.purpose == "Newer purpose"  # Should restore the latest

    def test_restore_returns_none_for_nonexistent_session(self, archive_repository):
        """Test that restore returns None for a non-existent session ID."""
        restored_session = archive_repository.restore("nonexistent-session-id")
        assert restored_session is None

    def test_restore_uses_file_lock(self, archive_repository, sample_session):
        """Test that restore uses file locking."""
        # First, save a backup so there's something to restore
        archive_repository.save(sample_session)

        with patch(
            "pipe.core.repositories.archive_repository.file_lock"
        ) as mock_file_lock:  # Changed patch target
            archive_repository.restore(sample_session.session_id)
            mock_file_lock.assert_called_once()

    def test_restore_handles_corrupted_json(self, archive_repository, sample_session):
        """Test that restore handles corrupted JSON files gracefully."""
        session_hash = hashlib.sha256(
            sample_session.session_id.encode("utf-8")
        ).hexdigest()
        corrupted_filename = (
            f"{session_hash}-20250101T000000.000000+0900.json"  # Added microseconds
        )
        corrupted_path = os.path.join(
            archive_repository.backups_dir, corrupted_filename
        )
        os.makedirs(os.path.dirname(corrupted_path), exist_ok=True)
        with open(corrupted_path, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        restored_session = archive_repository.restore(sample_session.session_id)
        assert restored_session is None


class TestArchiveRepositoryDelete:
    """Test ArchiveRepository.delete() method (using SHA256 hash and file_lock)."""

    def test_delete_all_backups_for_existing_session_id(
        self, archive_repository, sample_session
    ):
        """Test deleting all backups for a given session ID."""
        # Save multiple backups for the same session
        archive_repository.save(sample_session)
        with patch(
            "pipe.core.utils.datetime.get_current_timestamp"
        ) as mock_get_current_timestamp:
            mock_get_current_timestamp.return_value = datetime(
                2025,
                1,
                2,
                0,
                0,
                0,
                000000,
                tzinfo=zoneinfo.ZoneInfo("Asia/Tokyo"),  # Added microseconds
            )
            archive_repository.save(
                sample_session.model_copy(update={"purpose": "Second backup"})
            )

        # Save a backup for another session
        other_session = sample_session.model_copy(
            update={"session_id": "other-session"}
        )
        archive_repository.save(other_session)

        deleted = archive_repository.delete(sample_session.session_id)
        assert deleted is True
        assert (
            archive_repository.restore(sample_session.session_id) is None
        )  # No backups should remain
        assert (
            archive_repository.restore(other_session.session_id) is not None
        )  # Other session backup should remain

    def test_delete_returns_false_for_nonexistent_session_id(self, archive_repository):
        """Test that delete returns False for a non-existent session ID."""
        deleted = archive_repository.delete("nonexistent-session-id")
        assert deleted is False

    def test_delete_uses_file_lock(self, archive_repository, sample_session):
        """Test that delete uses file locking."""
        archive_repository.save(sample_session)  # Create a backup to delete
        with patch(
            "pipe.core.repositories.archive_repository.file_lock"
        ) as mock_file_lock:  # Changed patch target
            archive_repository.delete(sample_session.session_id)
            mock_file_lock.assert_called_once()

    def test_delete_handles_os_error_during_file_removal(
        self, archive_repository, sample_session
    ):
        """Test that delete handles OSError during file removal gracefully."""
        archive_repository.save(sample_session)

        with patch("os.remove") as mock_os_remove:
            mock_os_remove.side_effect = OSError("Permission denied")
            deleted = archive_repository.delete(sample_session.session_id)
            assert deleted is False  # Should not report as deleted if error occurs
            mock_os_remove.assert_called_once()
            # The file should still exist if permission denied
            assert archive_repository.restore(sample_session.session_id) is not None


class TestArchiveRepositoryExtractDeletedAt:
    """Test ArchiveRepository._extract_deleted_at() private method."""

    def test_extract_deleted_at_valid_filename(self, archive_repository):
        """Test extracting timestamp from a valid filename."""
        filename = "hash-2025-12-14T103045.123456+0900.json"
        expected_isoformat = "2025-12-14T10:30:45.123456+09:00"
        extracted = archive_repository._extract_deleted_at(filename)
        assert extracted == expected_isoformat

    def test_extract_deleted_at_invalid_filename_returns_none(self, archive_repository):
        """Test extracting timestamp from an invalid filename returns None."""
        filename = "hash-invalid-timestamp.json"
        extracted = archive_repository._extract_deleted_at(filename)
        assert extracted is None

        filename_no_timestamp = "hash.json"
        extracted = archive_repository._extract_deleted_at(filename_no_timestamp)
        assert extracted is None

        filename_wrong_format = "hash-20251214103045.json"
        extracted = archive_repository._extract_deleted_at(filename_wrong_format)
        assert extracted is None

    def test_extract_deleted_at_different_timezone_offset(self, archive_repository):
        """Test extracting timestamp with a different timezone offset."""
        filename = "hash-2025-12-14T103045.123456-0500.json"
        expected_isoformat = "2025-12-14T10:30:45.123456-05:00"
        extracted = archive_repository._extract_deleted_at(filename)
        assert extracted == expected_isoformat
