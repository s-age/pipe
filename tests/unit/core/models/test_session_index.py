import json

import pytest
from pipe.core.models.session_index import SessionIndex, SessionIndexEntry
from pydantic import ValidationError


class TestSessionIndexEntry:
    """SessionIndexEntry model validation and serialization tests."""

    def test_valid_entry_creation(self):
        """Test creating a valid session index entry."""
        entry = SessionIndexEntry(
            created_at="2025-01-01T00:00:00+09:00",
            last_updated_at="2025-01-01T01:00:00+09:00",
            purpose="Test purpose",
        )
        assert entry.created_at == "2025-01-01T00:00:00+09:00"
        assert entry.last_updated_at == "2025-01-01T01:00:00+09:00"
        assert entry.purpose == "Test purpose"

    def test_entry_validation_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SessionIndexEntry(created_at="2025-01-01T00:00:00+09:00")
        # Field name in error message will be the alias 'lastUpdatedAt'
        assert "lastUpdatedAt" in str(exc_info.value)

    def test_entry_serialization_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        entry = SessionIndexEntry(
            created_at="2025-01-01T00:00:00+09:00",
            last_updated_at="2025-01-01T01:00:00+09:00",
        )
        dumped = entry.model_dump(by_alias=True)
        assert dumped["createdAt"] == "2025-01-01T00:00:00+09:00"
        assert dumped["lastUpdatedAt"] == "2025-01-01T01:00:00+09:00"

    def test_entry_deserialization_from_camel_case(self):
        """Test that model can be validated from camelCase data."""
        data = {
            "createdAt": "2025-01-01T00:00:00+09:00",
            "lastUpdatedAt": "2025-01-01T01:00:00+09:00",
            "purpose": "Test",
        }
        entry = SessionIndexEntry.model_validate(data)
        assert entry.created_at == "2025-01-01T00:00:00+09:00"
        assert entry.last_updated_at == "2025-01-01T01:00:00+09:00"


class TestSessionIndex:
    """SessionIndex model validation, serialization, and logic tests."""

    @pytest.fixture
    def sample_entry(self):
        """Provide a sample SessionIndexEntry."""
        return SessionIndexEntry(
            created_at="2025-01-01T00:00:00+09:00",
            last_updated_at="2025-01-01T01:00:00+09:00",
            purpose="Sample",
        )

    def test_empty_index_creation(self):
        """Test creating an empty session index with defaults."""
        index = SessionIndex()
        assert index.sessions == {}
        assert index.version == "1.0"

    def test_add_and_get_session(self, sample_entry):
        """Test add_session and get_session methods."""
        index = SessionIndex()
        session_id = "session-123"
        index.add_session(session_id, sample_entry)

        assert index.contains_session(session_id) is True
        assert index.get_session(session_id) == sample_entry
        assert index.get_all_session_ids() == [session_id]

    def test_remove_session(self, sample_entry):
        """Test remove_session method."""
        index = SessionIndex()
        session_id = "session-123"
        index.add_session(session_id, sample_entry)

        assert index.remove_session(session_id) is True
        assert index.contains_session(session_id) is False
        assert index.remove_session("non-existent") is False

    def test_get_sessions_sorted_by_last_updated(self):
        """Test sorting sessions by last_updated_at descending."""
        index = SessionIndex()
        e1 = SessionIndexEntry(
            created_at="2025-01-01T00:00:00Z", last_updated_at="2025-01-01T10:00:00Z"
        )
        e2 = SessionIndexEntry(
            created_at="2025-01-01T00:00:00Z", last_updated_at="2025-01-01T12:00:00Z"
        )
        e3 = SessionIndexEntry(
            created_at="2025-01-01T00:00:00Z", last_updated_at="2025-01-01T08:00:00Z"
        )

        index.add_session("s1", e1)
        index.add_session("s2", e2)
        index.add_session("s3", e3)

        sorted_sessions = index.get_sessions_sorted_by_last_updated()
        # Should be s2 (12:00), s1 (10:00), s3 (08:00)
        assert sorted_sessions[0][0] == "s2"
        assert sorted_sessions[1][0] == "s1"
        assert sorted_sessions[2][0] == "s3"

    def test_get_child_sessions(self, sample_entry):
        """Test get_child_sessions method."""
        index = SessionIndex()
        index.add_session("parent", sample_entry)
        index.add_session("parent/child1", sample_entry)
        index.add_session("parent/child2", sample_entry)
        index.add_session("other", sample_entry)

        children = index.get_child_sessions("parent")
        assert len(children) == 2
        assert "parent/child1" in children
        assert "parent/child2" in children
        assert "other" not in children

    def test_remove_session_tree(self, sample_entry):
        """Test remove_session_tree method removes session and its children."""
        index = SessionIndex()
        index.add_session("parent", sample_entry)
        index.add_session("parent/child1", sample_entry)
        index.add_session("parent/child2", sample_entry)
        index.add_session("other", sample_entry)

        removed_count = index.remove_session_tree("parent")
        assert removed_count == 3
        assert index.contains_session("parent") is False
        assert index.contains_session("parent/child1") is False
        assert index.contains_session("parent/child2") is False
        assert index.contains_session("other") is True

    def test_roundtrip_serialization(self, sample_entry):
        """Test that serialization and deserialization preserve data."""
        original = SessionIndex(version="2.0")
        original.add_session("s1", sample_entry)

        # Serialize to JSON string with camelCase
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = SessionIndex.model_validate(data)

        # Verify
        assert restored.version == "2.0"
        assert restored.contains_session("s1")
        assert restored.get_session("s1").created_at == sample_entry.created_at
        assert restored.get_session("s1").purpose == sample_entry.purpose
