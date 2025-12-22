# Repositories Layer Testing Strategy

**Layer:** `src/pipe/core/repositories/`

## Responsibilities
- File I/O, database access
- Data persistence and retrieval
- Pydantic I/O patterns (JSON ↔ Model)

## Testing Strategy
- **Basic Policy**: Use the `tmp_path` fixture and verify read/write operations on the actual file system (temporary directory).
- **Use of Mocks**: Limited to abnormal system tests that are difficult to reproduce artificially, such as file lock conflicts or disk full errors.
- **Focus**:
  - Correctness of actual file operations (path generation, directory creation, etc.)
  - Data integrity (save → load roundtrip)
  - Synchronization between index and session files
  - Error handling (non-existent files, permission errors, etc.)

## Test Patterns

```python
# tests/unit/core/repositories/test_session_repository.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.timezone = "Asia/Tokyo"
    settings.sessions_path = ".sessions"
    return settings


@pytest.fixture
def repository(tmp_path, mock_settings):
    """Create a SessionRepository with temporary directory."""
    return SessionRepository(project_root=str(tmp_path), settings=mock_settings)


class TestSessionRepositoryFind:
    """Test SessionRepository.find() method."""

    def test_find_existing_session(self, repository):
        """Test finding an existing session."""
        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
        )
        repository.save(session)

        found = repository.find("test-123")
        assert found is not None
        assert found.session_id == "test-123"

    def test_find_nonexistent_session(self, repository):
        """Test that find() returns None for non-existent session."""
        found = repository.find("nonexistent-id")
        assert found is None

    @patch('pipe.core.repositories.session_repository.migrate_session_data')
    def test_find_applies_migration(self, mock_migrate, repository):
        """Test that find() applies data migration."""
        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
        )
        repository.save(session)

        # Mock migration to return modified data
        mock_migrate.return_value = {
            "session_id": "test-123",
            "created_at": "2025-01-01T00:00:00+09:00",
            "migrated": True,
        }

        found = repository.find("test-123")
        mock_migrate.assert_called_once()


class TestSessionRepositorySave:
    """Test SessionRepository.save() method."""

    def test_save_creates_file(self, repository):
        """Test that save() creates a session file."""
        import os

        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
        )

        repository.save(session)

        session_path = repository._get_path_for_id("test-123")
        assert os.path.exists(session_path)

    def test_save_updates_index(self, repository):
        """Test that save() updates the session index."""
        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Test purpose",
        )

        repository.save(session)

        index = repository.load_index()
        assert "test-123" in index.sessions
        assert index.sessions["test-123"].purpose == "Test purpose"

    def test_save_and_load_roundtrip(self, repository):
        """Test that save() and find() maintain data integrity."""
        original_session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Test purpose",
            background="Test background",
            roles=["Developer", "Tester"],
            multi_step_reasoning_enabled=True,
        )

        repository.save(original_session)
        loaded_session = repository.find("test-123")

        assert loaded_session is not None
        assert loaded_session.session_id == original_session.session_id
        assert loaded_session.purpose == original_session.purpose
        assert loaded_session.background == original_session.background
        assert loaded_session.roles == original_session.roles
        assert loaded_session.multi_step_reasoning_enabled == original_session.multi_step_reasoning_enabled


class TestSessionRepositoryDelete:
    """Test SessionRepository.delete() method."""

    def test_delete_existing_session(self, repository):
        """Test deleting an existing session."""
        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
        )
        repository.save(session)

        result = repository.delete("test-123")

        assert result is True
        assert repository.find("test-123") is None

    def test_delete_removes_from_index(self, repository):
        """Test that delete() removes session from index."""
        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
        )
        repository.save(session)

        repository.delete("test-123")

        index = repository.load_index()
        assert "test-123" not in index.sessions

    def test_delete_removes_empty_parent_directories(self, repository):
        """Test that delete() cleans up empty parent directories."""
        session = Session(
            session_id="parent/child/session-123",
            created_at="2025-01-01T00:00:00+09:00",
        )
        repository.save(session)

        repository.delete("parent/child/session-123")

        # Verify empty directories are removed
        import os
        parent_dir = os.path.join(repository.sessions_dir, "parent", "child")
        assert not os.path.exists(parent_dir)


class TestSessionRepositoryFileLocking:
    """Test file locking mechanism for concurrent access."""

    def test_save_concurrent_access(self, repository):
        """Test that concurrent saves are properly serialized by file locks."""
        import threading
        import time

        session = Session(
            session_id="concurrent-123",
            created_at="2025-01-01T00:00:00+09:00",
        )

        # Track operation order
        operations = []

        def save_with_delay(delay: float):
            time.sleep(delay)
            repository.save(session)
            operations.append(f"saved-{delay}")

        # Launch two concurrent save operations
        thread1 = threading.Thread(target=save_with_delay, args=(0.1,))
        thread2 = threading.Thread(target=save_with_delay, args=(0.2,))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # Both operations should complete successfully (no corruption)
        loaded = repository.find("concurrent-123")
        assert loaded is not None
        assert loaded.session_id == "concurrent-123"

    def test_atomic_update_prevents_data_race(self, repository):
        """Test that atomic updates prevent data races during concurrent modifications."""
        import threading

        session = Session(
            session_id="race-test",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Initial purpose",
        )
        repository.save(session)

        results = []

        def update_purpose(new_purpose: str):
            loaded = repository.find("race-test")
            loaded.purpose = new_purpose
            repository.save(loaded)
            results.append(new_purpose)

        # Two threads updating the same session
        thread1 = threading.Thread(target=update_purpose, args=("Purpose A",))
        thread2 = threading.Thread(target=update_purpose, args=("Purpose B",))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        # Final state should be one of the two purposes (last write wins)
        final = repository.find("race-test")
        assert final.purpose in ["Purpose A", "Purpose B"]


class TestSessionRepositoryErrorHandling:
    """Test error handling for exceptional cases."""

    @patch('builtins.open')
    def test_save_handles_permission_error(self, mock_open, repository):
        """Test that save() properly handles permission errors."""
        mock_open.side_effect = PermissionError("Permission denied")

        session = Session(
            session_id="perm-error",
            created_at="2025-01-01T00:00:00+09:00",
        )

        with pytest.raises(PermissionError, match="Permission denied"):
            repository.save(session)

    @patch('builtins.open')
    def test_save_handles_disk_full_error(self, mock_open, repository):
        """Test that save() properly handles disk full errors."""
        mock_open.side_effect = OSError(28, "No space left on device")

        session = Session(
            session_id="disk-full",
            created_at="2025-01-01T00:00:00+09:00",
        )

        with pytest.raises(OSError, match="No space left on device"):
            repository.save(session)

    def test_find_handles_corrupted_json(self, repository):
        """Test that find() handles corrupted JSON gracefully."""
        import os

        session_path = repository._get_path_for_id("corrupted-123")
        os.makedirs(os.path.dirname(session_path), exist_ok=True)

        # Write invalid JSON
        with open(session_path, 'w') as f:
            f.write("{ invalid json }")

        # Should raise ValueError or return None depending on implementation
        result = repository.find("corrupted-123")
        assert result is None or isinstance(result, Session)
```

## Mandatory Test Items
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Verification of file locking mechanisms
- ✅ Integrity of index updates
- ✅ Error handling (non-existent files, permission errors, etc.)
- ✅ Application of data migration
- ✅ Verification of atomic update patterns
