# Collections Layer Testing Strategy

**Layer:** `src/pipe/core/collections/`

## Responsibilities
- Abstraction of collection operations
- Wrappers for lists, dictionaries, etc.
- Collection-specific business logic

## Testing Strategy
- **No Mocks Needed**: Pure collection operations
- **Focus**: Correctness of add, delete, search, and filtering operations

## Test Patterns

```python
# tests/unit/core/collections/test_turns.py
import pytest
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.turn import UserTaskTurn, ModelResponseTurn


class TestTurnCollection:
    """Test TurnCollection operations."""

    def test_append_turn(self):
        """Test appending a turn to the collection."""
        collection = TurnCollection()
        turn = UserTaskTurn(
            type="user_task",
            instruction="Test",
            timestamp="2025-01-01T00:00:00+09:00",
        )
        collection.append(turn)

        assert len(collection) == 1
        assert collection[0] == turn

    def test_iteration(self):
        """Test iterating over turns."""
        turns = [
            UserTaskTurn(type="user_task", instruction="1", timestamp="2025-01-01T00:00:00+09:00"),
            ModelResponseTurn(type="model_response", content="2", timestamp="2025-01-01T00:01:00+09:00"),
        ]
        collection = TurnCollection(turns)

        iterated = list(collection)
        assert len(iterated) == 2
        assert iterated[0].instruction == "1"
        assert iterated[1].content == "2"

    def test_slicing(self):
        """Test slicing a TurnCollection."""
        turns = [
            UserTaskTurn(type="user_task", instruction=f"{i}", timestamp="2025-01-01T00:00:00+09:00")
            for i in range(5)
        ]
        collection = TurnCollection(turns)

        sliced = collection[:3]
        assert len(sliced) == 3
        assert sliced[0].instruction == "0"
```

## Mandatory Test Items
- ✅ Adding and removing elements
- ✅ Index access and slicing
- ✅ Iteration
- ✅ Search and filtering
- ✅ Behavior of empty collections
