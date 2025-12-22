# Domains Layer Testing Strategy

**Layer:** `src/pipe/core/domains/`

## Responsibilities
- Implementation of business logic
- **Pure functions containing no I/O operations**
- Data transformation, calculation, and verification

## Testing Strategy
- **No Mocks Needed**: Testing pure functions (no side effects)
- **Focus**: Logic correctness, edge cases, error handling

## Test Patterns

```python
# tests/unit/core/domains/test_session.py
import pytest
import zoneinfo
from pipe.core.domains.session import fork_session, initialize_session_references
from pipe.core.models.session import Session
from pipe.core.models.turn import ModelResponseTurn
from pipe.core.collections.turns import TurnCollection
from pipe.core.collections.references import ReferenceCollection


class TestForkSession:
    """Test fork_session domain logic."""

    def test_fork_session_valid(self):
        """Test forking a session at a valid model_response turn."""
        original = Session(
            session_id="original-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Original purpose",
            background="Original background",
            turns=TurnCollection([
                ModelResponseTurn(
                    type="model_response",
                    content="Response 1",
                    timestamp="2025-01-01T00:00:00+09:00",
                ),
            ]),
        )

        timezone_obj = zoneinfo.ZoneInfo("Asia/Tokyo")
        forked = fork_session(original, fork_index=0, timezone_obj=timezone_obj)

        assert forked.session_id != original.session_id
        assert forked.purpose == "Fork of: Original purpose"
        assert len(forked.turns) == 1
        assert forked.background == original.background

    def test_fork_session_invalid_index_out_of_range(self):
        """Test that fork_session raises IndexError for out-of-range index."""
        original = Session(
            session_id="original-123",
            created_at="2025-01-01T00:00:00+09:00",
            turns=TurnCollection([]),
        )

        with pytest.raises(IndexError, match="fork_index .* is out of range"):
            fork_session(original, fork_index=10, timezone_obj=zoneinfo.ZoneInfo("UTC"))

    def test_fork_session_invalid_turn_type(self):
        """Test that fork_session raises ValueError for non-model_response turn."""
        from pipe.core.models.turn import UserTaskTurn

        original = Session(
            session_id="original-123",
            created_at="2025-01-01T00:00:00+09:00",
            turns=TurnCollection([
                UserTaskTurn(
                    type="user_task",
                    instruction="Do something",
                    timestamp="2025-01-01T00:00:00+09:00",
                ),
            ]),
        )

        with pytest.raises(ValueError, match="Forking is only allowed from a 'model_response' turn"):
            fork_session(original, fork_index=0, timezone_obj=zoneinfo.ZoneInfo("UTC"))

    def test_fork_session_preserves_hierarchical_id(self):
        """Test that fork_session preserves hierarchical session IDs."""
        original = Session(
            session_id="parent/child-123",
            created_at="2025-01-01T00:00:00+09:00",
            turns=TurnCollection([
                ModelResponseTurn(
                    type="model_response",
                    content="Response",
                    timestamp="2025-01-01T00:00:00+09:00",
                ),
            ]),
        )

        forked = fork_session(original, fork_index=0, timezone_obj=zoneinfo.ZoneInfo("UTC"))
        assert forked.session_id.startswith("parent/")


class TestInitializeSessionReferences:
    """Test initialize_session_references domain logic."""

    def test_initialize_references_with_ttl(self):
        """Test that references are initialized with correct TTL."""
        references = ReferenceCollection()
        initialize_session_references(references, reference_ttl=5)

        assert references.default_ttl == 5

    def test_initialize_references_none_collection(self):
        """Test that None references are handled gracefully."""
        # Should not raise an exception
        initialize_session_references(None, reference_ttl=5)


class TestForkSessionImmutability:
    """Test that fork_session preserves immutability of the original session."""

    def test_fork_session_does_not_mutate_original(self):
        """Test that fork_session does not modify the original session."""
        original = Session(
            session_id="immutable-test",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Original purpose",
            background="Original background",
            roles=["Developer"],
            turns=TurnCollection([
                ModelResponseTurn(
                    type="model_response",
                    content="Response 1",
                    timestamp="2025-01-01T00:00:00+09:00",
                ),
                ModelResponseTurn(
                    type="model_response",
                    content="Response 2",
                    timestamp="2025-01-01T00:01:00+09:00",
                ),
            ]),
        )

        # Create a deep copy to compare later
        original_copy = original.model_copy(deep=True)

        # Fork the session
        timezone_obj = zoneinfo.ZoneInfo("Asia/Tokyo")
        forked = fork_session(original, fork_index=1, timezone_obj=timezone_obj)

        # Verify original is unchanged
        assert original.session_id == original_copy.session_id
        assert original.purpose == original_copy.purpose
        assert len(original.turns) == len(original_copy.turns)
        assert original.turns[0].content == "Response 1"
        assert original.turns[1].content == "Response 2"

        # Verify forked is different
        assert forked.session_id != original.session_id
        assert forked.purpose != original.purpose
        assert len(forked.turns) == 2  # fork_index + 1
```

## Mandatory Test Items
- ✅ Verification of normal logic
- ✅ Boundary value tests (empty arrays, out-of-range indexes, etc.)
- ✅ Error cases (`ValueError`, `IndexError`, etc.)
- ✅ Correctness of data transformation
- ✅ Guarantee of immutability (original data is not modified)
