import hashlib
import json
import os
import zoneinfo
from datetime import datetime
from unittest.mock import patch

import pytest
from pipe.core.repositories.archive_repository import ArchiveRepository, SessionSummary
from pydantic import ValidationError

from tests.factories.models.session_factory import SessionFactory


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
    """Create a sample Session object for testing using SessionFactory."""
    return SessionFactory.create(
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
        timestamp = "2025-01-01T00:00:00.000000+09:00"
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
        timestamp = "2025-01-01T00:00:00.000000+09:00"
        backup_path = archive_repository.save_backup(
            sample_session.session_id, sample_session, timestamp
        )

        with open(backup_path, encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == sample_session.model_dump(mode="json")


class TestArchiveRepositoryListBackups:
    """Test ArchiveRepository.list_backups() method."""

    def test_list_backups_for_existing_session(
        self, archive_repository, sample_session
    ):
        """Test listing backups for an existing session."""
        timestamps = [
            "2025-01-01T00:00:00.000000+09:00",
            "2025-01-02T00:00:00.000000+09:00",
        ]
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


class TestArchiveRepositoryRestoreBackup:
    """Test ArchiveRepository.restore_backup() method."""

    def test_restore_existing_backup(self, archive_repository, sample_session):
        """Test restoring an existing backup file."""
        timestamp = "2025-01-01T00:00:00.000000+09:00"
        backup_path = archive_repository.save_backup(
            sample_session.session_id, sample_session, timestamp
        )

        restored_session = archive_repository.restore_backup(backup_path)
        assert restored_session.session_id == sample_session.session_id
        assert restored_session.purpose == sample_session.purpose

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

        with pytest.raises(ValidationError):
            archive_repository.restore_backup(str(invalid_data_path))


class TestArchiveRepositoryDeleteBackup:
    """Test ArchiveRepository.delete_backup() method."""

    def test_delete_existing_backup(self, archive_repository, sample_session):
        """Test deleting an existing backup file."""
        timestamp = "2025-01-01T00:00:00.000000+09:00"
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
        ]
        for ts in timestamps:
            archive_repository.save_backup(
                sample_session.session_id, sample_session, ts
            )

        deleted_count = archive_repository.delete_all_backups(sample_session.session_id)
        assert deleted_count == 2
        assert len(archive_repository.list_backups(sample_session.session_id)) == 0


class TestArchiveRepositoryList:
    """Test ArchiveRepository.list() method."""

    def test_list_no_backups(self, archive_repository):
        """Test listing when no backups exist."""
        summaries = archive_repository.list()
        assert len(summaries) == 0

    def test_list_single_backup(self, archive_repository, sample_session):
        """Test listing a single backup."""
        timestamp = "2025-01-01T00:00:00.000000+09:00"
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

        archive_repository.save_backup(
            session_id_1,
            sample_session.model_copy(update={"session_id": session_id_1}),
            "2025-01-01T10:00:00.000000+09:00",
        )
        archive_repository.save_backup(
            session_id_2,
            sample_session.model_copy(update={"session_id": session_id_2}),
            "2025-01-02T11:00:00.000000+09:00",
        )

        summaries = archive_repository.list()
        assert len(summaries) == 2
        assert summaries[0].session_id == session_id_2
        assert summaries[1].session_id == session_id_1

    def test_list_skips_non_json_files(self, archive_repository, tmp_path):
        """Test that list() skips non-JSON files (covers line 183)."""
        non_json_path = tmp_path / "backups" / "not_a_backup.txt"
        os.makedirs(os.path.dirname(non_json_path), exist_ok=True)
        with open(non_json_path, "w") as f:
            f.write("text content")

        summaries = archive_repository.list()
        assert len(summaries) == 0

    def test_list_skips_corrupted_files(
        self, archive_repository, tmp_path, sample_session
    ):
        """Test that list() skips corrupted JSON files."""
        # Create a valid backup
        archive_repository.save_backup(
            sample_session.session_id,
            sample_session,
            "2025-01-01T00:00:00.000000+09:00",
        )

        # Create a corrupted file
        corrupted_path = tmp_path / "backups" / "corrupted.json"
        with open(corrupted_path, "w", encoding="utf-8") as f:
            f.write("{invalid json}")

        summaries = archive_repository.list()
        assert len(summaries) == 1

    def test_list_skips_missing_session_id(self, archive_repository, tmp_path):
        """Test that list() skips files with missing session_id."""
        path = tmp_path / "backups" / "missing_id_2025-01-01T000000.000000+0900.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"purpose": "no id"}, f)

        summaries = archive_repository.list()
        assert len(summaries) == 0


class TestArchiveRepositorySave:
    """Test ArchiveRepository.save() method."""

    @patch("pipe.core.repositories.archive_repository.get_current_timestamp")
    def test_save_creates_file(
        self, mock_get_current_timestamp, archive_repository, sample_session
    ):
        """Test that save creates a backup file with hash and timestamp."""
        mock_timestamp = "2025-01-01T10:30:45.123456+09:00"
        mock_get_current_timestamp.return_value = mock_timestamp

        backup_path = archive_repository.save(sample_session)

        session_hash = hashlib.sha256(
            sample_session.session_id.encode("utf-8")
        ).hexdigest()
        expected_filename_part = (
            f"{session_hash}-{mock_timestamp.replace(':', '')}.json"
        )
        assert expected_filename_part in backup_path
        assert os.path.exists(backup_path)

    def test_save_uses_file_lock(self, archive_repository, sample_session):
        """Test that save uses file locking."""
        with patch(
            "pipe.core.repositories.archive_repository.file_lock"
        ) as mock_file_lock:
            archive_repository.save(sample_session)
            mock_file_lock.assert_called_once()


class TestArchiveRepositoryRestore:
    """Test ArchiveRepository.restore() method."""

    def test_restore_latest(self, archive_repository, sample_session):
        """Test restoring the latest backup."""
        archive_repository.save_backup(
            sample_session.session_id,
            sample_session,
            "2025-01-01T00:00:00.000000+09:00",
        )

        newer_session = sample_session.model_copy(update={"purpose": "Newer"})
        with patch("pipe.core.utils.datetime.get_current_timestamp") as mock_ts:
            mock_ts.return_value = "2025-01-02T00:00:00.000000+09:00"
            archive_repository.save(newer_session)

        restored = archive_repository.restore(sample_session.session_id)
        assert restored is not None
        assert restored.purpose == "Newer"

    def test_restore_nonexistent(self, archive_repository):
        """Test that restore returns None for non-existent session."""
        assert archive_repository.restore("nonexistent") is None

    def test_restore_corrupted_returns_none(self, archive_repository, sample_session):
        """Test that restore returns None for corrupted JSON."""
        session_hash = hashlib.sha256(
            sample_session.session_id.encode("utf-8")
        ).hexdigest()
        corrupted_path = os.path.join(
            archive_repository.backups_dir,
            f"{session_hash}-20250101T000000.000000+0900.json",
        )
        os.makedirs(os.path.dirname(corrupted_path), exist_ok=True)
        with open(corrupted_path, "w") as f:
            f.write("{invalid json}")

        assert archive_repository.restore(sample_session.session_id) is None


class TestArchiveRepositoryDelete:
    """Test ArchiveRepository.delete() method."""

    def test_delete_existing(self, archive_repository, sample_session):
        """Test deleting backups for an existing session."""
        archive_repository.save(sample_session)
        assert archive_repository.delete(sample_session.session_id) is True
        assert archive_repository.restore(sample_session.session_id) is None

    def test_delete_nonexistent(self, archive_repository):
        """Test deleting a non-existent session returns False."""
        assert archive_repository.delete("nonexistent") is False

    @patch("os.remove")
    def test_delete_handles_os_error(
        self, mock_remove, archive_repository, sample_session
    ):
        """Test that delete handles OSError gracefully."""
        archive_repository.save(sample_session)
        mock_remove.side_effect = OSError("Permission denied")
        assert archive_repository.delete(sample_session.session_id) is False


class TestArchiveRepositoryExtractDeletedAt:
    """Test ArchiveRepository._extract_deleted_at() method."""

    def test_extract_valid(self, archive_repository):
        """Test extracting timestamp from a valid filename."""
        filename = "hash-2025-12-14T103045.123456+0900.json"
        expected = "2025-12-14T10:30:45.123456+09:00"
        assert archive_repository._extract_deleted_at(filename) == expected

    def test_extract_invalid_regex(self, archive_repository):
        """Test with filename that doesn't match regex."""
        assert archive_repository._extract_deleted_at("invalid.json") is None

    def test_extract_invalid_timestamp(self, archive_repository):
        """Test with filename that matches regex but is invalid date.

        Covers line 329.
        """
        # 99 is invalid month
        filename = "hash-2025-99-14T103045.123456+0900.json"
        assert archive_repository._extract_deleted_at(filename) is None
