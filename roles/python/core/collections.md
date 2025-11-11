# Collections Layer

## Purpose

Collections provide **specialized list-like containers** for managing groups of model objects. They focus on storage, retrieval, and iteration, while business logic resides in the domains layer.

## Responsibilities

1. **Specialized Storage** - Provide type-safe containers for specific models
2. **Iteration Support** - Enable pythonic iteration and indexing
3. **Collection Operations** - Append, extend, clear, copy
4. **Type Safety** - Ensure only valid items are stored
5. **Serialization** - Support conversion to/from lists

## Characteristics

- ✅ List-like interface
- ✅ Type-safe collections
- ✅ Support standard operations (append, extend, iter, len)
- ✅ Serialization support
- ✅ Immutable iteration patterns
- ❌ **NO business logic** - that belongs in domains/
- ❌ **NO filtering/transformation** - collections are dumb containers
- ❌ **NO validation** - models handle validation

## File Structure

```
collections/
├── __init__.py
├── turns.py           # TurnCollection
├── references.py      # ReferenceCollection
└── sessions.py        # SessionCollection (for index)
```

## Dependencies

**Allowed:**

- ✅ `models/` - To store and type-check models
- ✅ Standard library (typing, collections.abc)

**Forbidden:**

- ❌ `services/` - Collections don't orchestrate
- ❌ `domains/` - Collections don't contain logic
- ❌ `repositories/` - Collections don't persist

## Template

```python
"""
Collection for [Model] objects.
"""

from typing import Iterator, overload
from pipe.core.models.some_model import SomeModel


class SomeCollection:
    """
    Specialized collection for SomeModel objects.

    This is a thin wrapper around a list providing:
    - Type safety
    - Iteration support
    - Serialization

    Business logic belongs in domains/, not here.
    """

    def __init__(self, items: list[SomeModel] | None = None):
        """
        Initialize collection.

        Args:
            items: Initial items (empty list if None)
        """
        self._items: list[SomeModel] = items or []

    def append(self, item: SomeModel) -> None:
        """
        Adds item to collection.

        Args:
            item: Item to add
        """
        self._items.append(item)

    def extend(self, items: list[SomeModel]) -> None:
        """
        Adds multiple items.

        Args:
            items: Items to add
        """
        self._items.extend(items)

    def clear(self) -> None:
        """Removes all items."""
        self._items.clear()

    def copy(self) -> "SomeCollection":
        """
        Creates shallow copy.

        Returns:
            New collection with copied list
        """
        return SomeCollection(self._items.copy())

    def to_list(self) -> list[SomeModel]:
        """
        Converts to plain list.

        Returns:
            List of items
        """
        return self._items.copy()

    # Iteration support
    def __iter__(self) -> Iterator[SomeModel]:
        """Enables iteration over collection."""
        return iter(self._items)

    def __len__(self) -> int:
        """Returns number of items."""
        return len(self._items)

    def __getitem__(self, index: int | slice) -> SomeModel | list[SomeModel]:
        """
        Gets item(s) by index or slice.

        Args:
            index: Integer index or slice

        Returns:
            Single item or list of items
        """
        return self._items[index]

    def __setitem__(self, index: int, value: SomeModel) -> None:
        """
        Sets item at index.

        Args:
            index: Position to set
            value: New value
        """
        self._items[index] = value

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}({len(self._items)} items)"
```

## Real Examples

### TurnCollection - Conversation History

**Key Characteristics:**

- Stores Turn objects in chronological order
- Supports slicing for history windows
- Maintains turn order integrity
- Used in Session model

```python
"""
Collection for Turn objects.
"""

from typing import Iterator
from pipe.core.models.turn import Turn


class TurnCollection:
    """
    Specialized collection for Turn objects.

    Maintains chronological order of conversation turns.
    Business logic for filtering/transforming turns belongs in domains/turns.py.
    """

    def __init__(self, turns: list[Turn] | None = None):
        """
        Initialize turn collection.

        Args:
            turns: Initial turns (empty list if None)
        """
        self._turns: list[Turn] = turns or []

    def append(self, turn: Turn) -> None:
        """
        Adds turn to end of collection.

        Args:
            turn: Turn to add
        """
        self._turns.append(turn)

    def extend(self, turns: list[Turn]) -> None:
        """
        Adds multiple turns.

        Args:
            turns: Turns to add
        """
        self._turns.extend(turns)

    def clear(self) -> None:
        """Removes all turns."""
        self._turns.clear()

    def copy(self) -> "TurnCollection":
        """
        Creates shallow copy.

        Returns:
            New collection with copied list
        """
        return TurnCollection(self._turns.copy())

    def to_list(self) -> list[Turn]:
        """
        Converts to plain list.

        Returns:
            List of turns
        """
        return self._turns.copy()

    # Iteration and indexing
    def __iter__(self) -> Iterator[Turn]:
        """Enables iteration over turns."""
        return iter(self._turns)

    def __len__(self) -> int:
        """Returns number of turns."""
        return len(self._turns)

    def __getitem__(self, index: int | slice) -> Turn | list[Turn]:
        """
        Gets turn(s) by index or slice.

        Examples:
            collection[0]        # First turn
            collection[-1]       # Last turn
            collection[1:5]      # Turns 1-4
            collection[:-1]      # All except last

        Args:
            index: Integer index or slice

        Returns:
            Single turn or list of turns
        """
        result = self._turns[index]

        # If slice, wrap in new collection
        if isinstance(index, slice):
            return result
        return result

    def __setitem__(self, index: int, value: Turn) -> None:
        """
        Replaces turn at index.

        Args:
            index: Position to set
            value: New turn
        """
        self._turns[index] = value

    def __repr__(self) -> str:
        """String representation."""
        return f"TurnCollection({len(self._turns)} turns)"
```

### ReferenceCollection - File References

**Key Characteristics:**

- Stores Reference objects with TTL
- Supports finding by path
- Maintains reference list
- TTL decay happens in domains/

```python
"""
Collection for Reference objects.
"""

from typing import Iterator
from pipe.core.models.reference import Reference


class ReferenceCollection:
    """
    Specialized collection for Reference objects.

    Stores file references with TTL information.
    Business logic for TTL decay belongs in domains/references.py.
    """

    def __init__(self, references: list[Reference] | None = None):
        """
        Initialize reference collection.

        Args:
            references: Initial references (empty list if None)
        """
        self._references: list[Reference] = references or []

    def append(self, reference: Reference) -> None:
        """
        Adds reference to collection.

        Args:
            reference: Reference to add
        """
        self._references.append(reference)

    def extend(self, references: list[Reference]) -> None:
        """
        Adds multiple references.

        Args:
            references: References to add
        """
        self._references.extend(references)

    def clear(self) -> None:
        """Removes all references."""
        self._references.clear()

    def copy(self) -> "ReferenceCollection":
        """
        Creates shallow copy.

        Returns:
            New collection with copied list
        """
        return ReferenceCollection(self._references.copy())

    def find_by_path(self, path: str) -> Reference | None:
        """
        Finds reference by path.

        This is a simple lookup, not business logic.

        Args:
            path: File path to search for

        Returns:
            Reference if found, None otherwise
        """
        for ref in self._references:
            if ref.path == path:
                return ref
        return None

    def to_list(self) -> list[Reference]:
        """
        Converts to plain list.

        Returns:
            List of references
        """
        return self._references.copy()

    # Iteration and indexing
    def __iter__(self) -> Iterator[Reference]:
        """Enables iteration over references."""
        return iter(self._references)

    def __len__(self) -> int:
        """Returns number of references."""
        return len(self._references)

    def __getitem__(self, index: int) -> Reference:
        """
        Gets reference by index.

        Args:
            index: Position

        Returns:
            Reference at index
        """
        return self._references[index]

    def __setitem__(self, index: int, value: Reference) -> None:
        """
        Replaces reference at index.

        Args:
            index: Position to set
            value: New reference
        """
        self._references[index] = value

    def __repr__(self) -> str:
        """String representation."""
        return f"ReferenceCollection({len(self._references)} references)"
```

### SessionCollection - Session Index

```python
"""
Collection for Session metadata (index).
"""

from typing import Iterator


class SessionMetadata:
    """Lightweight session metadata for index."""

    def __init__(
        self,
        id: str,
        purpose: str,
        created_at: str,
        updated_at: str,
        turn_count: int,
        parent_id: str | None = None,
    ):
        self.id = id
        self.purpose = purpose
        self.created_at = created_at
        self.updated_at = updated_at
        self.turn_count = turn_count
        self.parent_id = parent_id


class SessionCollection:
    """
    Collection for session metadata.

    Used for session index/catalog, not for full session objects.
    Full sessions are loaded individually via SessionRepository.
    """

    def __init__(self, sessions: list[SessionMetadata] | None = None):
        """
        Initialize session collection.

        Args:
            sessions: Initial session metadata
        """
        self._sessions: list[SessionMetadata] = sessions or []

    def append(self, session: SessionMetadata) -> None:
        """Adds session metadata."""
        self._sessions.append(session)

    def find_by_id(self, session_id: str) -> SessionMetadata | None:
        """
        Finds session metadata by ID.

        Args:
            session_id: Session ID to find

        Returns:
            SessionMetadata if found, None otherwise
        """
        for session in self._sessions:
            if session.id == session_id:
                return session
        return None

    def find_children(self, parent_id: str) -> list[SessionMetadata]:
        """
        Finds all child sessions of a parent.

        Args:
            parent_id: Parent session ID

        Returns:
            List of child session metadata
        """
        return [s for s in self._sessions if s.parent_id == parent_id]

    def to_list(self) -> list[SessionMetadata]:
        """Converts to plain list."""
        return self._sessions.copy()

    def __iter__(self) -> Iterator[SessionMetadata]:
        """Enables iteration."""
        return iter(self._sessions)

    def __len__(self) -> int:
        """Returns number of sessions."""
        return len(self._sessions)

    def __repr__(self) -> str:
        """String representation."""
        return f"SessionCollection({len(self._sessions)} sessions)"
```

## Collection Patterns

### Pattern 1: Safe Rebuild

Collections support safe rebuild pattern used in domains:

```python
# Domain logic uses this pattern
def modify_collection(collection: SomeCollection) -> None:
    """Domain function that rebuilds collection safely."""
    new_items = []

    for item in collection:
        modified_item = transform(item)
        new_items.append(modified_item)

    # Safe rebuild
    collection.clear()
    collection.extend(new_items)
```

### Pattern 2: Slicing Support

```python
# Collections support Python slicing
turns = TurnCollection([turn1, turn2, turn3, turn4, turn5])

recent_turns = turns[-3:]      # Last 3 turns
history = turns[:-1]            # All except last
window = turns[1:4]             # Turns 1-3
```

### Pattern 3: Type-Safe Iteration

```python
# Type hints work correctly
def process_turns(turns: TurnCollection) -> None:
    for turn in turns:
        # 'turn' is properly typed as Turn
        print(turn.timestamp)
```

## Testing

### Unit Testing Collections

```python
# tests/core/collections/test_turns.py
from pipe.core.collections.turns import TurnCollection
from pipe.core.models.turn import UserTaskTurn

def test_turn_collection_append():
    collection = TurnCollection()
    turn = UserTaskTurn(message="Test", timestamp="2024-01-01T00:00:00")

    collection.append(turn)

    assert len(collection) == 1
    assert collection[0] == turn


def test_turn_collection_iteration():
    turns = [
        UserTaskTurn(message=f"Task {i}", timestamp="2024-01-01T00:00:00")
        for i in range(3)
    ]
    collection = TurnCollection(turns)

    # Test iteration
    result = list(collection)
    assert len(result) == 3
    assert result[0].message == "Task 0"


def test_turn_collection_slicing():
    turns = [
        UserTaskTurn(message=f"Task {i}", timestamp="2024-01-01T00:00:00")
        for i in range(5)
    ]
    collection = TurnCollection(turns)

    # Test slicing
    last_three = collection[-3:]
    assert len(last_three) == 3
    assert last_three[0].message == "Task 2"


def test_reference_collection_find_by_path():
    from pipe.core.collections.references import ReferenceCollection
    from pipe.core.models.reference import Reference

    refs = [
        Reference(path="file1.py", ttl=5),
        Reference(path="file2.py", ttl=3),
    ]
    collection = ReferenceCollection(refs)

    found = collection.find_by_path("file1.py")
    assert found is not None
    assert found.ttl == 5

    not_found = collection.find_by_path("file3.py")
    assert not_found is None


def test_collection_copy():
    turns = [
        UserTaskTurn(message="Task", timestamp="2024-01-01T00:00:00")
    ]
    collection = TurnCollection(turns)

    # Copy should be independent
    copy = collection.copy()
    copy.append(UserTaskTurn(message="New", timestamp="2024-01-01T00:00:00"))

    assert len(collection) == 1
    assert len(copy) == 2
```

## Best Practices

### 1. Keep Collections Dumb

```python
# ✅ GOOD: Collection is just storage
class TurnCollection:
    def append(self, turn: Turn) -> None:
        self._turns.append(turn)

# ❌ BAD: Collection contains business logic
class TurnCollection:
    def append(self, turn: Turn) -> None:
        # Business logic doesn't belong here
        if len(self._turns) > 100:
            self._turns = self._turns[-50:]  # This is business logic!
        self._turns.append(turn)
```

### 2. Support Standard Python Protocols

```python
# ✅ GOOD: Implement __iter__, __len__, __getitem__
class Collection:
    def __iter__(self): ...
    def __len__(self): ...
    def __getitem__(self, index): ...

# ❌ BAD: Custom methods that don't follow Python conventions
class Collection:
    def get_all(self): ...  # Use __iter__ instead
    def get_count(self): ...  # Use __len__ instead
```

### 3. Simple Lookups OK, Complex Logic in Domains

```python
# ✅ GOOD: Simple lookup method
def find_by_path(self, path: str) -> Reference | None:
    for ref in self._references:
        if ref.path == path:
            return ref
    return None

# ❌ BAD: Complex filtering belongs in domains
def get_active_references(self) -> list[Reference]:
    # This is business logic - belongs in domains/references.py
    return [ref for ref in self._references if ref.ttl > 0 or ref.persistent]
```

### 4. Immutable Iteration

```python
# ✅ GOOD: Return copies to prevent external mutation
def to_list(self) -> list[Item]:
    return self._items.copy()

# ❌ BAD: Expose internal list
def to_list(self) -> list[Item]:
    return self._items  # Caller can mutate internal state!
```

## Summary

Collections are **type-safe containers**:

- ✅ List-like interface
- ✅ Type safety
- ✅ Standard Python protocols
- ✅ Support for domains/ patterns
- ❌ No business logic
- ❌ No transformation
- ❌ No validation

Collections are **dumb storage** - they hold items and let you iterate over them. That's it.
