# Services Layer Testing Strategy

**Layer:** `src/pipe/core/services/`

## Responsibilities
- Implementation of use cases
- Coordination between multiple Repositories/Domains
- Orchestration of business flow

## Testing Strategy
- **Mock the Repository Layer**: Mock dependencies from lower layers.
- **Focus**: Use case logic, interaction between layers, error propagation.
- **State Management**: If the Service holds instance variables (e.g., `current_session`), create a new instance for each test using fixtures to prevent state leakage between tests.

## Test Patterns

```python
# tests/unit/core/services/test_session_service.py
import pytest
from unittest.mock import Mock, patch
from pipe.core.services.session_service import SessionService
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.models.args import TaktArgs


@pytest.fixture
def mock_repository():
    """Create a mock SessionRepository."""
    return Mock(spec=SessionRepository)


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = Mock(spec=Settings)
    settings.timezone = "Asia/Tokyo"
    settings.reference_ttl = 3
    return settings


@pytest.fixture
def service(mock_repository, mock_settings):
    """Create SessionService with mocked dependencies.

    IMPORTANT: This fixture creates a new SessionService instance for each test
    to prevent state leakage between tests (e.g., current_session, current_session_id).
    """
    return SessionService(
        project_root="/tmp/test",
        settings=mock_settings,
        repository=mock_repository,
    )


class TestSessionServiceGetSession:
    """Test SessionService.get_session() method."""

    def test_get_existing_session(self, service, mock_repository):
        """Test getting an existing session."""
        expected_session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
        )
        mock_repository.find.return_value = expected_session

        result = service.get_session("test-123")

        assert result == expected_session
        mock_repository.find.assert_called_once_with("test-123")

    def test_get_nonexistent_session(self, service, mock_repository):
        """Test that get_session returns None for non-existent session."""
        mock_repository.find.return_value = None

        result = service.get_session("nonexistent")

        assert result is None


class TestSessionServicePrepare:
    """Test SessionService.prepare() method."""

    def test_prepare_with_existing_session(self, service, mock_repository):
        """Test prepare() with an existing session ID."""
        existing_session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Existing",
            background="Background",
        )
        mock_repository.find.return_value = existing_session

        args = TaktArgs(
            session="test-123",
            instruction="New instruction",
        )

        service.prepare(args)

        assert service.current_session == existing_session
        assert service.current_session_id == "test-123"
        mock_repository.find.assert_called_once_with("test-123")

    def test_prepare_creates_new_session(self, service, mock_repository):
        """Test prepare() creates a new session when session ID is not provided."""
        args = TaktArgs(
            purpose="New session",
            background="Background",
            instruction="First instruction",
        )

        service.prepare(args)

        assert service.current_session is not None
        assert service.current_session.purpose == "New session"
        mock_repository.save.assert_called_once()

    def test_prepare_raises_error_for_nonexistent_session(self, service, mock_repository):
        """Test that prepare() raises FileNotFoundError for non-existent session."""
        mock_repository.find.return_value = None

        args = TaktArgs(session="nonexistent", instruction="Test")

        with pytest.raises(FileNotFoundError, match="Session with ID 'nonexistent' not found"):
            service.prepare(args)

    def test_prepare_adds_references(self, service, mock_repository):
        """Test that prepare() adds references from args."""
        args = TaktArgs(
            purpose="Test",
            background="Background",
            instruction="Test",
            references=["file1.py", "file2.py"],
            references_persist=["file1.py"],
        )

        service.prepare(args)

        session = service.current_session
        assert len(session.references) == 2
        # Verify persistent reference
        file1_ref = next((r for r in session.references if r.path == "file1.py"), None)
        assert file1_ref is not None
        assert file1_ref.persist is True


class TestSessionServiceCreateNewSession:
    """Test SessionService.create_new_session() method."""

    def test_create_new_session(self, service, mock_repository):
        """Test creating a new session."""
        session = service.create_new_session(
            purpose="Test",
            background="Background",
            roles=["Developer"],
        )

        assert session.purpose == "Test"
        assert session.background == "Background"
        assert session.roles == ["Developer"]
        mock_repository.save.assert_called_once_with(session)

    @patch('pipe.core.services.session_service.FileIndexerService')
    def test_create_new_session_rebuilds_index(self, mock_indexer_cls, service, mock_repository):
        """Test that creating a new session triggers index rebuild."""
        mock_indexer = Mock()
        service.file_indexer_service = mock_indexer

        service.create_new_session(
            purpose="Test",
            background="Background",
            roles=[],
        )

        mock_indexer.create_index.assert_called_once()


class TestSessionServiceDeleteSession:
    """Test SessionService.delete_session() method."""

    def test_delete_session(self, service, mock_repository):
        """Test deleting a session."""
        service.delete_session("test-123")

        mock_repository.delete.assert_called_once_with("test-123")

    def test_delete_sessions_bulk(self, service, mock_repository):
        """Test bulk deletion of sessions."""
        mock_repository.delete.side_effect = [True, True, Exception("Error")]

        deleted_count = service.delete_sessions(["id1", "id2", "id3"])

        assert deleted_count == 2  # Two successful deletions
        assert mock_repository.delete.call_count == 3
```

## Mandatory Test Items
- ✅ Verification of major use cases
- ✅ Mocking of Repository layer
- ✅ Verification of error propagation
- ✅ Verification of multi-layer interaction
- ✅ Consistency of transactional operations
