"""Unit tests for SessionTreeService."""

from unittest.mock import MagicMock

import pytest
from pipe.core.models.results.session_tree_result import SessionTreeResult
from pipe.core.models.session_index import SessionIndex, SessionIndexEntry
from pipe.core.services.session_tree_service import SessionTreeService

from tests.factories.models import create_test_settings


@pytest.fixture
def mock_repository():
    """Create a mock SessionRepository."""
    return MagicMock()


@pytest.fixture
def settings():
    """Create test settings."""
    return create_test_settings()


@pytest.fixture
def service(mock_repository, settings):
    """Create SessionTreeService with mocked dependencies."""
    return SessionTreeService(repository=mock_repository, settings=settings)


class TestSessionTreeServiceInit:
    """Test SessionTreeService initialization."""

    def test_init(self, mock_repository, settings):
        """Test that service is initialized correctly."""
        service = SessionTreeService(repository=mock_repository, settings=settings)
        assert service.repository == mock_repository
        assert service.settings == settings


class TestSessionTreeServiceGetSessionTree:
    """Test SessionTreeService.get_session_tree() method."""

    def test_get_session_tree_empty(self, service, mock_repository):
        """Test building tree from an empty index."""
        mock_index = MagicMock(spec=SessionIndex)
        mock_index.get_sessions_sorted_by_last_updated.return_value = []
        mock_repository.load_index.return_value = mock_index

        result = service.get_session_tree()

        assert isinstance(result, SessionTreeResult)
        assert result.sessions == {}
        assert result.session_tree == []

    def test_get_session_tree_flat(self, service, mock_repository):
        """Test building tree with only root sessions (no hierarchy)."""
        entry1 = SessionIndexEntry(
            created_at="2025-01-01T00:00:00Z",
            last_updated_at="2025-01-01T01:00:00Z",
            purpose="Session 1",
        )
        entry2 = SessionIndexEntry(
            created_at="2025-01-01T00:00:00Z",
            last_updated_at="2025-01-01T02:00:00Z",
            purpose="Session 2",
        )

        mock_index = MagicMock(spec=SessionIndex)
        # Sorted by last_updated_at DESC
        mock_index.get_sessions_sorted_by_last_updated.return_value = [
            ("session2", entry2),
            ("session1", entry1),
        ]
        mock_repository.load_index.return_value = mock_index

        result = service.get_session_tree()

        assert len(result.sessions) == 2
        assert result.sessions["session1"].purpose == "Session 1"
        assert result.sessions["session2"].purpose == "Session 2"

        assert len(result.session_tree) == 2
        assert result.session_tree[0].session_id == "session2"
        assert result.session_tree[1].session_id == "session1"
        assert result.session_tree[0].children == []
        assert result.session_tree[1].children == []

    def test_get_session_tree_hierarchical(self, service, mock_repository):
        """Test building tree with parent-child relationships."""
        parent_entry = SessionIndexEntry(
            created_at="2025-01-01T00:00:00Z",
            last_updated_at="2025-01-01T01:00:00Z",
            purpose="Parent",
        )
        child_entry = SessionIndexEntry(
            created_at="2025-01-01T00:30:00Z",
            last_updated_at="2025-01-01T01:30:00Z",
            purpose="Child",
        )

        mock_index = MagicMock(spec=SessionIndex)
        # Sorted by last_updated_at DESC
        mock_index.get_sessions_sorted_by_last_updated.return_value = [
            ("parent/child", child_entry),
            ("parent", parent_entry),
        ]
        mock_repository.load_index.return_value = mock_index

        result = service.get_session_tree()

        assert len(result.sessions) == 2
        assert len(result.session_tree) == 1

        root = result.session_tree[0]
        assert root.session_id == "parent"
        assert len(root.children) == 1
        assert root.children[0].session_id == "parent/child"

    def test_get_session_tree_missing_parent(self, service, mock_repository):
        """Test that child with missing parent in index is treated as root."""
        child_entry = SessionIndexEntry(
            created_at="2025-01-01T00:30:00Z",
            last_updated_at="2025-01-01T01:30:00Z",
            purpose="Child",
        )

        mock_index = MagicMock(spec=SessionIndex)
        mock_index.get_sessions_sorted_by_last_updated.return_value = [
            ("parent/child", child_entry),
        ]
        mock_repository.load_index.return_value = mock_index

        result = service.get_session_tree()

        assert len(result.session_tree) == 1
        assert result.session_tree[0].session_id == "parent/child"

    def test_get_session_tree_deep_nesting(self, service, mock_repository):
        """Test building tree with multiple levels of nesting."""
        root_entry = SessionIndexEntry(
            created_at="2025-01-01T00:00:00Z",
            last_updated_at="2025-01-01T01:00:00Z",
        )
        child_entry = SessionIndexEntry(
            created_at="2025-01-01T01:00:00Z",
            last_updated_at="2025-01-01T02:00:00Z",
        )
        grandchild_entry = SessionIndexEntry(
            created_at="2025-01-01T02:00:00Z",
            last_updated_at="2025-01-01T03:00:00Z",
        )

        mock_index = MagicMock(spec=SessionIndex)
        mock_index.get_sessions_sorted_by_last_updated.return_value = [
            ("a/b/c", grandchild_entry),
            ("a/b", child_entry),
            ("a", root_entry),
        ]
        mock_repository.load_index.return_value = mock_index

        result = service.get_session_tree()

        assert len(result.session_tree) == 1
        root = result.session_tree[0]
        assert root.session_id == "a"
        assert len(root.children) == 1

        child = root.children[0]
        assert child.session_id == "a/b"
        assert len(child.children) == 1

        grandchild = child.children[0]
        assert grandchild.session_id == "a/b/c"
        assert len(grandchild.children) == 0

    def test_get_session_tree_skips_empty_id(self, service, mock_repository):
        """Test that empty session IDs are skipped in the tree but included in the sessions map."""
        entry = SessionIndexEntry(
            created_at="2025-01-01T00:00:00Z",
            last_updated_at="2025-01-01T01:00:00Z",
        )

        mock_index = MagicMock(spec=SessionIndex)
        mock_index.get_sessions_sorted_by_last_updated.return_value = [
            ("", entry),
            ("valid", entry),
        ]
        mock_repository.load_index.return_value = mock_index

        result = service.get_session_tree()

        # Note: Current implementation skips empty IDs for the tree nodes
        # but includes them in the sessions dictionary.
        assert len(result.sessions) == 2
        assert "valid" in result.sessions
        assert "" in result.sessions
        assert len(result.session_tree) == 1
        assert result.session_tree[0].session_id == "valid"
