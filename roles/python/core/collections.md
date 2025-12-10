# Collections Layer

## Purpose

Collections provide **type-safe list-like containers** for managing groups of model objects. They handle storage and iteration while delegating business logic to domains.

## Responsibilities

1. **Type-Safe Storage** - Container for specific model types
2. **Iteration** - Support pythonic iteration and indexing
3. **Basic Operations** - Add, remove, clear, copy
4. **Self-Management** - Collections can enforce their own invariants
5. **Serialization** - Convert to/from lists

## Rules

### ✅ DO

- Provide list-like interface (append, extend, iter, len, indexing)
- Enforce type safety
- Support serialization (to_list, from_list)
- Add self-management methods when needed (add, edit_by_index, delete_by_index)
- Keep methods simple and focused

### ❌ DON'T

- **NO complex business logic** - Use domains/
- **NO filtering/transformation** - Collections are containers, domains handle logic
- **NO validation beyond type checking** - Models validate data
- **NO persistence** - Collections are in-memory structures

## File Structure

```
collections/
├── turns.py           # TurnCollection (self-managing)
├── references.py      # ReferenceCollection (self-managing)
└── sessions.py        # SessionCollection (for index)
```

## Dependencies

**Allowed:**
- ✅ models/ - Store and type-check models
- ✅ Standard library (typing, collections.abc)

**Forbidden:**
- ❌ services/ - Collections don't orchestrate
- ❌ domains/ - Collections don't contain logic (but can call domains)
- ❌ repositories/ - Collections don't persist

## Example: Self-Managing Collection

```python
"""Collection for Turn objects."""

from typing import Iterator, overload
from pipe.core.models.turn import Turn

class TurnCollection:
    """
    Self-managing collection for Turn objects.
    
    Inspired by ReferenceCollection pattern, this collection
    can manage its own items (add, edit, delete) while keeping
    complex business logic in domains/.
    """
    
    def __init__(self, turns: list[Turn] | None = None):
        self._turns = list(turns) if turns else []
    
    # Basic list operations
    def append(self, turn: Turn) -> None:
        """Add turn to end."""
        self._turns.append(turn)
    
    def extend(self, turns: list[Turn]) -> None:
        """Add multiple turns."""
        self._turns.extend(turns)
    
    def clear(self) -> None:
        """Remove all turns."""
        self._turns.clear()
    
    # Self-management methods
    def add(self, turn: Turn) -> None:
        """
        Add turn with validation.
        
        Business Rules:
        - Turn must be valid Turn instance
        - Added to end of collection
        """
        if not isinstance(turn, Turn):
            raise TypeError("Must be Turn instance")
        self._turns.append(turn)
    
    def edit_by_index(self, index: int, data: dict) -> None:
        """
        Edit turn at index.
        
        Args:
            index: Turn index to edit
            data: New turn data
            
        Raises:
            IndexError: If index out of range
        """
        if not (0 <= index < len(self._turns)):
            raise IndexError(f"Index {index} out of range")
        
        # Create new turn with updated data
        old_turn = self._turns[index]
        updated_data = old_turn.model_dump()
        updated_data.update(data)
        self._turns[index] = Turn(**updated_data)
    
    def delete_by_index(self, index: int) -> None:
        """
        Delete turn at index.
        
        Args:
            index: Turn index to delete
            
        Raises:
            IndexError: If index out of range
        """
        if not (0 <= index < len(self._turns)):
            raise IndexError(f"Index {index} out of range")
        del self._turns[index]
    
    def merge_from(self, other: "TurnCollection") -> None:
        """
        Merge turns from another collection.
        
        Args:
            other: Collection to merge from
        """
        self._turns.extend(other._turns)
    
    # Pythonic interface
    def __len__(self) -> int:
        return len(self._turns)
    
    def __iter__(self) -> Iterator[Turn]:
        return iter(self._turns)
    
    @overload
    def __getitem__(self, index: int) -> Turn: ...
    @overload
    def __getitem__(self, index: slice) -> list[Turn]: ...
    
    def __getitem__(self, index: int | slice) -> Turn | list[Turn]:
        return self._turns[index]
    
    # Serialization
    def to_list(self) -> list[dict]:
        """Convert to list of dicts."""
        return [turn.model_dump() for turn in self._turns]
    
    @classmethod
    def from_list(cls, data: list[dict]) -> "TurnCollection":
        """Create from list of dicts."""
        turns = [Turn(**item) for item in data]
        return cls(turns)
```

## Example: Simple Collection

```python
"""Collection for Session objects (for index)."""

from typing import Iterator
from pipe.core.models.session import Session

class SessionCollection:
    """
    Simple collection for Session objects.
    
    Used for session index/list operations.
    No self-management needed - sessions managed via repository.
    """
    
    def __init__(self, sessions: list[Session] | None = None):
        self._sessions = list(sessions) if sessions else []
    
    def append(self, session: Session) -> None:
        self._sessions.append(session)
    
    def __len__(self) -> int:
        return len(self._sessions)
    
    def __iter__(self) -> Iterator[Session]:
        return iter(self._sessions)
    
    def to_list(self) -> list[dict]:
        return [s.model_dump() for s in self._sessions]
```

## Common Patterns

### Pattern 1: Self-Management

```python
def add(self, item: Model) -> None:
    """Add with validation."""
    if not isinstance(item, Model):
        raise TypeError("Wrong type")
    self._items.append(item)
```

### Pattern 2: Index Validation

```python
def edit_by_index(self, index: int, data: dict) -> None:
    """Edit with range check."""
    if not (0 <= index < len(self._items)):
        raise IndexError(f"Index {index} out of range")
    # Update logic
```

### Pattern 3: Immutable Iteration

```python
def __iter__(self) -> Iterator[Model]:
    """Iterate safely."""
    return iter(self._items)  # Returns iterator, not mutable list
```

## Testing

```python
# tests/core/collections/test_turns.py

def test_add_appends_turn():
    """Test add appends to collection."""
    collection = TurnCollection()
    turn = Turn(type="user_input", content="test")
    
    collection.add(turn)
    
    assert len(collection) == 1
    assert collection[0] == turn

def test_edit_by_index_updates_turn():
    """Test edit_by_index updates turn data."""
    turn = Turn(type="user_input", content="original")
    collection = TurnCollection([turn])
    
    collection.edit_by_index(0, {"content": "updated"})
    
    assert collection[0].content == "updated"

def test_delete_by_index_removes_turn():
    """Test delete_by_index removes turn."""
    turns = [Turn(type="user_input", content=f"turn{i}") for i in range(3)]
    collection = TurnCollection(turns)
    
    collection.delete_by_index(1)
    
    assert len(collection) == 2
    assert collection[0].content == "turn0"
    assert collection[1].content == "turn2"

def test_edit_by_index_raises_on_invalid_index():
    """Test edit_by_index validates range."""
    collection = TurnCollection()
    
    with pytest.raises(IndexError):
        collection.edit_by_index(0, {})
```

## Summary

**Collections:**
- ✅ Type-safe list-like containers
- ✅ Pythonic iteration (iter, len, indexing)
- ✅ Self-management methods when needed
- ✅ Serialization support
- ❌ No complex logic, filtering, or persistence
- ❌ Business logic belongs in domains/

**Collections manage storage, domains manage logic**
