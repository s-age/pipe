"""Unit tests for session domain logic."""

import zoneinfo
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.domains.session import (
    destroy_session,
    fork_session,
    initialize_session_references,
)

from tests.factories.models import ReferenceFactory, SessionFactory, TurnFactory


class TestForkSession:
    """Tests for fork_session function."""

    @freeze_time("2025-01-01 12:00:00")
    def test_fork_session_success(self):
        """Test successful session forking."""
        # Setup
        timezone = zoneinfo.ZoneInfo("UTC")
        turns = [
            TurnFactory.create_user_task(instruction="Task 1"),
            TurnFactory.create_model_response(content="Response 1"),
            TurnFactory.create_user_task(instruction="Task 2"),
            TurnFactory.create_model_response(content="Response 2"),
        ]
        original = SessionFactory.create(
            session_id="original-id",
            purpose="Original Purpose",
            turns=TurnCollection(turns),
            cumulative_total_tokens=1000,
            todos=[{"title": "Todo 1", "checked": False}],
        )

        # Execute
        # Fork at index 1 (Response 1)
        forked = fork_session(original, fork_index=1, timezone_obj=timezone)

        # Verify
        assert forked.session_id != original.session_id
        assert "/" not in forked.session_id  # No parent path
        assert forked.purpose == "Fork of: Original Purpose"
        assert forked.created_at == "2025-01-01T12:00:00+00:00"
        assert len(forked.turns) == 2
        assert forked.turns[0].instruction == "Task 1"
        assert forked.turns[1].content == "Response 1"
        assert forked.cumulative_total_tokens == 0
        assert forked.cumulative_cached_tokens == 0
        assert len(forked.todos) == 1
        assert forked.todos[0].title == "Todo 1"
        # Verify deep copy of todos
        # Note: fork_session uses .copy() which is shallow for list of objects.
        assert forked.todos is not original.todos

    def test_fork_session_hierarchical_id(self):
        """Test session forking with hierarchical session ID."""
        # Setup
        timezone = zoneinfo.ZoneInfo("UTC")
        turns = [TurnFactory.create_model_response(content="Response 1")]
        original = SessionFactory.create(
            session_id="parent/child-id",
            turns=TurnCollection(turns),
        )

        # Execute
        forked = fork_session(original, fork_index=0, timezone_obj=timezone)

        # Verify
        assert forked.session_id.startswith("parent/")
        assert len(forked.session_id.split("/")) == 2

    def test_fork_session_index_out_of_range(self):
        """Test forking with out-of-range index."""
        timezone = zoneinfo.ZoneInfo("UTC")
        original = SessionFactory.create(turns=TurnCollection([]))

        with pytest.raises(IndexError, match=r"fork_index 0 is out of range"):
            fork_session(original, fork_index=0, timezone_obj=timezone)

    def test_fork_session_invalid_turn_type(self):
        """Test forking from a non-model_response turn."""
        timezone = zoneinfo.ZoneInfo("UTC")
        turns = [TurnFactory.create_user_task(instruction="Task 1")]
        original = SessionFactory.create(turns=TurnCollection(turns))

        with pytest.raises(
            ValueError, match="Forking is only allowed from a 'model_response' turn"
        ):
            fork_session(original, fork_index=0, timezone_obj=timezone)

    def test_fork_session_immutability(self):
        """Test that original session is not mutated."""
        timezone = zoneinfo.ZoneInfo("UTC")
        turns = [TurnFactory.create_model_response(content="Response 1")]
        original = SessionFactory.create(
            session_id="original",
            turns=TurnCollection(turns),
        )
        original_copy = original.model_copy(deep=True)

        fork_session(original, fork_index=0, timezone_obj=timezone)

        assert original == original_copy

    def test_fork_session_references_ttl(self):
        """Test that references TTL is preserved."""
        timezone = zoneinfo.ZoneInfo("UTC")
        turns = TurnCollection([TurnFactory.create_model_response()])

        # Use a non-empty collection to ensure it's truthy
        references = ReferenceCollection([ReferenceFactory.create()])
        references.default_ttl = 10

        original = SessionFactory.create(turns=turns, references=references)

        forked = fork_session(original, fork_index=0, timezone_obj=timezone)

        assert forked.references.default_ttl == 10


class TestDestroySession:
    """Tests for destroy_session function."""

    def test_destroy_session_raises_not_implemented(self):
        """Test that destroy_session raises NotImplementedError."""
        mock_session = MagicMock()
        with pytest.raises(
            NotImplementedError, match=r"destroy_session\(\) is deprecated"
        ):
            destroy_session(mock_session)


class TestInitializeSessionReferences:
    """Tests for initialize_session_references function."""

    def test_initialize_references_success(self):
        """Test successful initialization of references."""
        # Use a non-empty collection to ensure it's truthy
        references = ReferenceCollection([ReferenceFactory.create()])
        initialize_session_references(references, reference_ttl=5)
        assert references.default_ttl == 5

    def test_initialize_references_none(self):
        """Test initialization with None references."""
        # Should not raise
        initialize_session_references(None, reference_ttl=5)
