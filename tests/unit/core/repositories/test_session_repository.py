"""Tests for SessionRepository."""

import json
import os
import shutil
from unittest.mock import Mock, patch

import pytest
from pipe.core.models.session_index import SessionIndexEntry
from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository

from tests.factories.models.session_factory import SessionFactory


@pytest.fixture
def mock_settings(tmp_path):
    """Create mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.timezone = "Asia/Tokyo"
    settings.sessions_path = ".sessions"
    return settings


@pytest.fixture
def repository(tmp_path, mock_settings):
    """Create a SessionRepository with temporary directory."""
    return SessionRepository(project_root=str(tmp_path), settings=mock_settings)


class TestSessionRepositoryInit:
    """Test SessionRepository initialization."""

    def test_init_creates_directories(self, tmp_path, mock_settings):
        """Test that initialization creates necessary directories."""

        SessionRepository(project_root=str(tmp_path), settings=mock_settings)

        assert os.path.exists(tmp_path / ".sessions")

        assert os.path.exists(tmp_path / ".sessions" / "backups")

    def test_init_with_invalid_timezone(self, tmp_path, mock_settings):
        """Test initialization with an invalid timezone (should fall back to UTC)."""

        mock_settings.timezone = "Invalid/Timezone"

        # This will print a warning to stderr, but should not crash

        repo = SessionRepository(project_root=str(tmp_path), settings=mock_settings)

        assert repo.timezone_obj.key == "UTC"


class TestSessionRepositoryFind:
    """Test SessionRepository.find() method."""

    def test_find_existing_session(self, repository):
        """Test finding an existing session."""

        session = SessionFactory.create(session_id="test-123")

        repository.save(session)

        found = repository.find("test-123")

        assert found is not None

        assert found.session_id == "test-123"

    def test_find_nonexistent_session(self, repository):
        """Test that find() returns None for non-existent session."""

        found = repository.find("nonexistent-id")

        assert found is None

    def test_find_handles_corrupted_json(self, repository):
        """Test that find() handles corrupted JSON by returning None."""

        session_id = "corrupted-123"

        session_path = repository._get_path_for_id(session_id)

        os.makedirs(os.path.dirname(session_path), exist_ok=True)

        with open(session_path, "w") as f:
            f.write("{ invalid json }")

        found = repository.find(session_id)

        assert found is None

    @patch("pipe.core.repositories.session_repository.migrate_session_data")
    def test_find_applies_migration(self, mock_migrate, repository):
        """Test that find() applies data migration."""

        session = SessionFactory.create(session_id="migrate-123")

        repository.save(session)

        # Mock migration to return modified data

        mock_migrate.side_effect = lambda data, tz: {**data, "purpose": "Migrated"}

        found = repository.find("migrate-123")

        assert found is not None

        assert found.purpose == "Migrated"

        mock_migrate.assert_called_once()


class TestSessionRepositorySave:
    """Test SessionRepository.save() method."""

    def test_save_creates_file(self, repository):
        """Test that save() creates a session file."""

        session = SessionFactory.create(session_id="save-123")

        repository.save(session)

        session_path = repository._get_path_for_id("save-123")

        assert os.path.exists(session_path)

        with open(session_path) as f:
            data = json.load(f)

            assert data["session_id"] == "save-123"

    def test_save_updates_index(self, repository):
        """Test that save() updates the session index."""

        session = SessionFactory.create(session_id="index-123", purpose="Test Purpose")

        repository.save(session)

        index = repository.load_index()

        assert "index-123" in index.sessions

        assert index.sessions["index-123"].purpose == "Test Purpose"

    def test_save_with_old_index_format(self, repository):
        """Test that save() migrates old index format.

        (last_updated -> last_updated_at).
        """

        # Create an old-format index

        old_index_data = {
            "sessions": {
                "old-session": {
                    "created_at": "2025-01-01T00:00:00+09:00",
                    "last_updated": "2025-01-01T01:00:00+09:00",
                    "purpose": "Old format",
                }
            }
        }

        with open(repository.index_path, "w") as f:
            json.dump(old_index_data, f)

        # Save a new session

        new_session = SessionFactory.create(session_id="new-session")

        repository.save(new_session)

        # Verify old session is migrated in memory/on disk

        index = repository.load_index()

        assert "old-session" in index.sessions

        assert (
            index.sessions["old-session"].last_updated_at == "2025-01-01T01:00:00+09:00"
        )

    def test_save_subfolder_id(self, repository):
        """Test that session ID with slashes creates subdirectories."""

        session_id = "parent/child/session-123"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        session_path = repository._get_path_for_id(session_id)

        assert os.path.exists(session_path)

        assert "parent/child" in session_path

    def test_save_with_redundant_index_format(self, repository):
        """Test that save() handles index entry.

        (with both last_updated and last_updated_at).
        """

        old_index_data = {
            "sessions": {
                "redundant-session": {
                    "created_at": "2025-01-01T00:00:00+09:00",
                    "last_updated": "2025-01-01T01:00:00+09:00",
                    "last_updated_at": "2025-01-01T02:00:00+09:00",
                    "purpose": "Redundant format",
                }
            }
        }

        with open(repository.index_path, "w") as f:
            json.dump(old_index_data, f)

        repository.save(SessionFactory.create(session_id="new-session"))

        index = repository.load_index()

        assert "redundant-session" in index.sessions

        # Should keep last_updated_at and remove last_updated

        assert (
            index.sessions["redundant-session"].last_updated_at
            == "2025-01-01T02:00:00+09:00"
        )

    def test_save_with_non_dict_entry_in_index(self, repository):
        """Test that save() handles non-dict entries in index (should not crash)."""

        # This is a bit of an edge case as JSON usually gives dicts

        old_index_data = {"sessions": {"invalid-entry": "not-a-dict"}}

        with open(repository.index_path, "w") as f:
            json.dump(old_index_data, f)

        # Should raise ValidationError because "not-a-dict" cannot be validated as
        # SessionIndexEntry

        with pytest.raises(Exception):
            repository.save(SessionFactory.create(session_id="any"))


class TestSessionRepositoryLoadIndex:
    """Test SessionRepository.load_index() method."""

    def test_load_index_empty(self, repository):
        """Test loading index when no sessions exist."""

        index = repository.load_index()

        assert len(index.sessions) == 0

    def test_load_index_migration(self, repository):
        """Test that load_index applies migration."""

        old_index_data = {
            "sessions": {
                "old-session": {
                    "created_at": "2025-01-01T00:00:00+09:00",
                    "last_updated": "2025-01-01T01:00:00+09:00",
                }
            }
        }

        with open(repository.index_path, "w") as f:
            json.dump(old_index_data, f)

        index = repository.load_index()

        assert (
            index.sessions["old-session"].last_updated_at == "2025-01-01T01:00:00+09:00"
        )


class TestSessionRepositoryDelete:
    """Test SessionRepository.delete() method."""

    def test_delete_removes_file_and_index(self, repository):
        """Test that delete() removes both session file and index entry."""

        session_id = "delete-123"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        result = repository.delete(session_id)

        assert result is True

        assert not os.path.exists(repository._get_path_for_id(session_id))

        index = repository.load_index()

        assert session_id not in index.sessions

    def test_delete_session_in_index_but_no_file(self, repository):
        """Test deleting a session that is in index but file is already gone."""

        session_id = "only-in-index"

        # Manually add to index

        index = repository.load_index()

        index.sessions[session_id] = SessionIndexEntry(
            created_at="2025-01-01T00:00:00+09:00",
            last_updated_at="2025-01-01T00:00:00+09:00",
        )

        repository._write_json(repository.index_path, index.model_dump(mode="json"))

        result = repository.delete(session_id)

        assert result is True

        assert session_id not in repository.load_index().sessions

    def test_delete_session_with_migration_in_index(self, repository):
        """Test that delete() applies migration to index before deleting."""

        session_id = "old-delete"

        old_index_data = {
            "sessions": {
                session_id: {
                    "created_at": "2025-01-01T00:00:00+09:00",
                    "last_updated": "2025-01-01T01:00:00+09:00",
                },
                "other": {
                    "created_at": "2025-01-01T00:00:00+09:00",
                    "last_updated": "2025-01-01T01:00:00+09:00",
                },
            }
        }

        with open(repository.index_path, "w") as f:
            json.dump(old_index_data, f)

        repository.delete(session_id)

        index = repository.load_index()

        assert session_id not in index.sessions

        assert "other" in index.sessions

        assert index.sessions["other"].last_updated_at == "2025-01-01T01:00:00+09:00"

    def test_delete_cleans_up_empty_directories(self, repository):
        """Test that delete() removes empty parent directories."""

        session_id = "a/b/c/session"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        repository.delete(session_id)

        # Check that 'a/b/c' is gone, but '.sessions' remains

        assert not os.path.exists(os.path.join(repository.sessions_dir, "a"))

        assert os.path.exists(repository.sessions_dir)

    def test_delete_handles_directory_cleanup_error(self, repository):
        """Test that delete() handles errors during directory cleanup gracefully."""

        session_id = "a/session"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        # Mock os.listdir to raise an error during cleanup

        with patch("os.listdir") as mock_listdir:
            # First call for delete file cleanup (optional, depends on implementation)

            # We want to trigger it during the directory removal loop

            mock_listdir.side_effect = [
                ["session.json", "session.json.lock"],
                OSError("Failed"),
            ]

            # Should not crash

            repository.delete(session_id)

    def test_delete_handles_file_removal_error(self, repository):
        """Test that delete() raises error if file removal fails."""

        session_id = "fail-delete"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        with patch("os.remove") as mock_remove:
            mock_remove.side_effect = OSError("Access denied")

            with pytest.raises(OSError, match="Access denied"):
                repository.delete(session_id)

        def test_delete_session_file_exists_but_not_in_index(self, repository):
            """Test deleting a session where file exists but not in index."""

            session_id = "file-only"

            session = SessionFactory.create(session_id=session_id)

            # Save manually to avoid index update if possible?

            # Actually save() always updates index.

            repository.save(session)

            # Manually remove from index

            index = repository.load_index()

            index.sessions.pop(session_id)

            repository._write_json(repository.index_path, index.model_dump(mode="json"))

            result = repository.delete(session_id)

            # Should return True because file existed and was deleted

            assert result is True

            assert not os.path.exists(repository._get_path_for_id(session_id))

        def test_delete_session_with_redundant_index_migration(self, repository):
            """Test delete migration.

            (when both last_updated and last_updated_at are present).
            """

            session_id = "redundant-delete"

            old_index_data = {
                "sessions": {
                    session_id: {
                        "created_at": "2025-01-01T00:00:00+09:00",
                        "last_updated": "2025-01-01T01:00:00+09:00",
                        "last_updated_at": "2025-01-01T02:00:00+09:00",
                    }
                }
            }

            with open(repository.index_path, "w") as f:
                json.dump(old_index_data, f)

            repository.delete(session_id)

            assert session_id not in repository.load_index().sessions

            def test_delete_session_not_in_index_but_file_deleted(self, repository):
                """Test delete return value.

                (when file is deleted but session was not in index).
                """

                session_id = "file-only-2"

                session_path = repository._get_path_for_id(session_id)

                os.makedirs(os.path.dirname(session_path), exist_ok=True)

                with open(session_path, "w") as f:
                    f.write("{}")

                # Session is not in index

                result = repository.delete(session_id)

                # Should return True because session_deleted was True

                assert result is True

            def test_delete_session_in_index_and_removed(self, repository):
                """Test delete return value when session is removed from index."""

                session_id = "in-index"

                session = SessionFactory.create(session_id=session_id)

                repository.save(session)

                # Remove file manually to ensure it's not deleted by file logic

                os.remove(repository._get_path_for_id(session_id))

                result = repository.delete(session_id)

                # Should return True because removed_count > 0

                assert result is True

            def test_delete_session_tree_in_index(self, repository):
                """Test delete session tree from index."""

                repository.save(SessionFactory.create(session_id="parent/s1"))

                repository.save(SessionFactory.create(session_id="parent/s2"))

                # Deleting parent should remove both from index

                result = repository.delete("parent")

                assert result is True

                index = repository.load_index()

                assert "parent/s1" not in index.sessions

                assert "parent/s2" not in index.sessions


class TestSessionRepositoryBackup:
    """Test backup related methods."""

    def test_backup_creates_file(self, repository):
        """Test that backup() creates a file in backups directory."""

        session_id = "backup-123"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        repository.backup(session)

        backups = [
            f for f in os.listdir(repository.backups_dir) if not f.endswith(".lock")
        ]

        assert len(backups) == 1

        assert backups[0].endswith(".json")

    def test_backup_nonexistent_file(self, repository):
        """Test that backup() does nothing if session file doesn't exist."""

        session = SessionFactory.create(session_id="no-file")

        repository.backup(session)

        assert len(os.listdir(repository.backups_dir)) == 0

    def test_move_to_backup(self, repository):
        """Test moving a session to backup."""

        session_id = "move-123"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        result = repository.move_to_backup(session_id)

        assert result is True

        assert not os.path.exists(repository._get_path_for_id(session_id))

        backups = [
            f for f in os.listdir(repository.backups_dir) if not f.endswith(".lock")
        ]

        assert len(backups) == 1

        assert session_id not in repository.load_index().sessions

    def test_move_to_backup_handles_exception(self, repository):
        """Test that move_to_backup returns False on exception."""

        session_id = "move-fail"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        with patch.object(repository, "backup", side_effect=Exception("Failed")):
            result = repository.move_to_backup(session_id)

            assert result is False

    def test_delete_backup(self, repository):
        """Test deleting a backup."""

        session_id = "del-backup-123"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        repository.backup(session)

        # Filter out .lock files

        backups = [
            f for f in os.listdir(repository.backups_dir) if not f.endswith(".lock")
        ]

        assert len(backups) == 1

        repository.delete_backup(session_id)

        backups = [
            f for f in os.listdir(repository.backups_dir) if not f.endswith(".lock")
        ]

        assert len(backups) == 0

    def test_delete_backup_handles_error(self, repository):
        """Test that delete_backup raises error if file removal fails."""

        session_id = "del-backup-fail"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        repository.backup(session)

        with patch("os.remove") as mock_remove:
            # The first call might be for the lock file depending on how it's called

            # but delete_backup calls os.remove(backup_path) inside the lock

            mock_remove.side_effect = OSError("Failed")

            with pytest.raises(OSError, match="Failed"):
                repository.delete_backup(session_id)

    def test_delete_backup_no_dir(self, repository):
        """Test delete_backup when backups directory doesn't exist."""

        shutil.rmtree(repository.backups_dir)

        # Should not crash

        repository.delete_backup("any")


class TestSessionRepositoryAtomicUpdate:
    """Test SessionRepository._atomic_update() method."""

    def test_atomic_update_modifies_session(self, repository):
        """Test that _atomic_update correctly modifies session data."""

        session_id = "atomic-123"

        session = SessionFactory.create(session_id=session_id, purpose="Old Purpose")

        repository.save(session)

        def update_purpose(s):
            s.purpose = "New Purpose"

        updated = repository._atomic_update(session_id, update_purpose)

        assert updated.purpose == "New Purpose"

        assert repository.find(session_id).purpose == "New Purpose"

    def test_atomic_update_nonexistent_session(self, repository):
        """Test _atomic_update on non-existent session."""

        with pytest.raises(FileNotFoundError, match="Session no-session not found"):
            repository._atomic_update("no-session", lambda s: None)

    def test_atomic_update_updates_index_metadata(self, repository):
        """Test that _atomic_update updates the last_updated_at in index."""

        session_id = "atomic-meta-123"

        session = SessionFactory.create(session_id=session_id)

        repository.save(session)

        initial_index = repository.load_index()

        initial_time = initial_index.sessions[session_id].last_updated_at

        # Ensure some time passes or just rely on the fact that save and update

        # call get_current_timestamp separately

        def noop(s):
            pass

        repository._atomic_update(session_id, noop)

        updated_index = repository.load_index()

        updated_time = updated_index.sessions[session_id].last_updated_at

        # They should be different as save and _atomic_update both set it

        assert updated_time != initial_time

    def test_update_index_metadata_nonexistent(self, repository):
        """Test _update_index_metadata on non-existent session in index."""

        # Should not crash or update anything

        repository._update_index_metadata("nonexistent")


class TestSessionRepositoryErrorHandling:
    """Test error handling in SessionRepository."""

    @patch("builtins.open")
    def test_save_handles_permission_error(self, mock_open, repository):
        """Test that save() propagates permission errors."""
        mock_open.side_effect = PermissionError("Permission denied")
        session = SessionFactory.create(session_id="perm-error")

        with pytest.raises(PermissionError, match="Permission denied"):
            repository.save(session)

    @patch("builtins.open")
    def test_save_handles_disk_full_error(self, mock_open, repository):
        """Test that save() propagates disk full errors."""
        mock_open.side_effect = OSError(28, "No space left on device")
        session = SessionFactory.create(session_id="disk-full")

        with pytest.raises(OSError, match="No space left on device"):
            repository.save(session)
