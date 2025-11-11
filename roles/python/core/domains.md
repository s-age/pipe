# Domains Layer

## Purpose

Domains contain **pure business logic** for manipulating core data entities. This layer implements the rules and behaviors that define how the system works, isolated from infrastructure concerns like persistence or external APIs.

## Responsibilities

1. **Business Rules** - Implement domain-specific rules and constraints
2. **Data Transformations** - Transform and filter data according to business logic
3. **Validation Logic** - Complex business validations
4. **State Transitions** - Define valid state changes
5. **Calculations** - Business calculations and derivations

## Characteristics

- ✅ Pure business logic functions
- ✅ Stateless transformations
- ✅ Work with collections and models
- ✅ Implement complex filtering and rules
- ✅ No side effects (no I/O, no persistence)
- ❌ **NO file operations** - domains are pure
- ❌ **NO API calls** - domains don't interact with external systems
- ❌ **NO persistence** - domains don't save data
- ❌ **NO dependency on services** - domains are low-level

## File Structure

```
domains/
├── __init__.py
├── artifacts.py      # Artifact management logic
├── references.py     # Reference TTL and filtering
├── todos.py          # Todo validation and filtering
└── turns.py          # Turn filtering and expiration
```

## Dependencies

**Allowed:**

- ✅ `models/` - To work with data structures
- ✅ `collections/` - To manipulate specialized collections
- ✅ `utils/` - For datetime, pure utilities

**Forbidden:**

- ❌ `services/` - Domains are called BY services
- ❌ `repositories/` - No persistence
- ❌ `agents/` - No external interactions
- ❌ `delegates/` - Wrong direction of dependency

## Template

```python
"""
Domain logic for [entity/concept].
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipe.core.models.some_model import SomeModel
    from pipe.core.collections.some_collection import SomeCollection


def apply_business_rule(
    entity: "SomeModel",
    parameter: str,
) -> "SomeModel":
    """
    Applies business rule to entity.

    This is a pure function that:
    1. Takes input data
    2. Applies business logic
    3. Returns new/modified data
    4. Has no side effects

    Args:
        entity: The entity to process
        parameter: Rule parameter

    Returns:
        Modified entity

    Raises:
        ValueError: If business rule is violated
    """
    # Validate business rule
    if not _is_valid(entity, parameter):
        raise ValueError(f"Business rule violated: {parameter}")

    # Apply transformation
    result = _transform(entity, parameter)

    return result


def filter_collection(
    collection: "SomeCollection",
    criteria: dict,
) -> list["SomeModel"]:
    """
    Filters collection according to business criteria.

    Args:
        collection: Collection to filter
        criteria: Business filtering criteria

    Returns:
        List of entities matching criteria
    """
    filtered = []
    for item in collection:
        if _matches_criteria(item, criteria):
            filtered.append(item)
    return filtered


def _is_valid(entity: "SomeModel", parameter: str) -> bool:
    """
    Internal validation helper.

    Private functions (prefixed with _) contain implementation details.
    """
    return len(parameter) > 0 and entity.status == "active"


def _transform(entity: "SomeModel", parameter: str) -> "SomeModel":
    """Internal transformation helper."""
    # Business logic implementation
    return entity.model_copy(update={"value": parameter})


def _matches_criteria(item: "SomeModel", criteria: dict) -> bool:
    """Internal filtering helper."""
    for key, value in criteria.items():
        if getattr(item, key) != value:
            return False
    return True
```

## Real Examples

### turns.py - Turn Filtering and Expiration

**Key Responsibilities:**

- Filter turns for prompt generation
- Limit tool response turns
- Expire old tool responses to save tokens
- Implement turn history optimization

```python
from collections.abc import Iterator
from typing import TYPE_CHECKING

from pipe.core.models.turn import ToolResponseTurn, Turn

if TYPE_CHECKING:
    from pipe.core.collections.turns import TurnCollection


def get_turns_for_prompt(
    turns_collection: "TurnCollection",
    tool_response_limit: int = 3
) -> Iterator[Turn]:
    """
    Yields turns for prompt generation, applying filtering rules.

    Business Rules:
    - The last turn (current task) is excluded
    - Only the last N 'tool_response' turns from history are included
    - This prevents context bloat from old tool outputs

    Args:
        turns_collection: Full turn history
        tool_response_limit: Maximum tool responses to include

    Yields:
        Turns suitable for prompt context
    """
    tool_response_count = 0
    history = turns_collection[:-1]  # Exclude the last turn

    # Iterate in reverse to easily count the last N tool_responses
    for turn in reversed(history):
        if isinstance(turn, ToolResponseTurn):
            tool_response_count += 1
            if tool_response_count > tool_response_limit:
                continue  # Skip old tool responses
        yield turn


def expire_old_tool_responses(
    turns_collection: "TurnCollection",
    expiration_threshold: int = 3
) -> bool:
    """
    Expires message content of old tool_response turns to save tokens.

    Business Rules:
    - Tool responses older than N user tasks are expired
    - Expired responses keep their 'succeeded' status
    - Recent tool responses are preserved for context

    This uses a safe rebuild pattern to avoid mutating during iteration.

    Args:
        turns_collection: Turn collection to process
        expiration_threshold: Number of recent user tasks to preserve

    Returns:
        True if any turns were modified
    """
    if not turns_collection:
        return False

    # Find user task turns
    user_tasks = [turn for turn in turns_collection if turn.type == "user_task"]
    if len(user_tasks) <= expiration_threshold:
        return False  # Not enough history to expire

    # Calculate expiration timestamp
    expiration_threshold_timestamp = user_tasks[-expiration_threshold].timestamp

    # Rebuild collection with expired turns
    new_turns = []
    modified = False

    for turn in turns_collection:
        if (
            isinstance(turn, ToolResponseTurn)
            and turn.timestamp < expiration_threshold_timestamp
            and turn.message  # Has content to expire
        ):
            # Expire this turn
            expired_turn = turn.model_copy(update={
                "message": "[Tool response expired to save tokens]"
            })
            new_turns.append(expired_turn)
            modified = True
        else:
            new_turns.append(turn)

    # Replace collection contents if modified
    if modified:
        turns_collection.clear()
        turns_collection.extend(new_turns)

    return modified


def count_turns_by_type(turns_collection: "TurnCollection") -> dict[str, int]:
    """
    Counts turns by type for analytics.

    Args:
        turns_collection: Turn collection to analyze

    Returns:
        Dictionary mapping turn type to count
    """
    counts: dict[str, int] = {}

    for turn in turns_collection:
        turn_type = turn.type
        counts[turn_type] = counts.get(turn_type, 0) + 1

    return counts
```

### references.py - Reference TTL Management

**Key Responsibilities:**

- Decay reference TTL over time
- Filter active vs expired references
- Add references with proper initialization
- Implement reference persistence rules

```python
from typing import TYPE_CHECKING

from pipe.core.models.reference import Reference

if TYPE_CHECKING:
    from pipe.core.collections.references import ReferenceCollection


def add_reference(
    references: "ReferenceCollection",
    path: str,
    persist: bool = False,
    initial_ttl: int = 5,
) -> Reference:
    """
    Adds a reference with proper TTL initialization.

    Business Rules:
    - Persistent references have TTL = -1 (never expire)
    - Regular references start with configurable TTL
    - Duplicate paths are not allowed

    Args:
        references: Reference collection
        path: File path to reference
        persist: Whether reference should persist across turns
        initial_ttl: Initial TTL for non-persistent references

    Returns:
        The created reference

    Raises:
        ValueError: If reference already exists
    """
    # Check for duplicates
    if any(ref.path == path for ref in references):
        raise ValueError(f"Reference already exists: {path}")

    # Create reference with appropriate TTL
    ttl = -1 if persist else initial_ttl

    reference = Reference(
        path=path,
        ttl=ttl,
        persistent=persist,
    )

    references.append(reference)
    return reference


def decay_reference_ttl(references: "ReferenceCollection") -> bool:
    """
    Decays TTL for all non-persistent references.

    Business Rules:
    - Persistent references (TTL = -1) are not affected
    - Regular references have TTL decremented by 1
    - References with TTL <= 0 are expired and removed

    Args:
        references: Reference collection to process

    Returns:
        True if any references were removed
    """
    initial_count = len(references)

    # Rebuild collection with decayed/filtered references
    active_refs = []

    for ref in references:
        if ref.persistent:
            # Persistent references never decay
            active_refs.append(ref)
        elif ref.ttl > 0:
            # Decay TTL
            decayed = ref.model_copy(update={"ttl": ref.ttl - 1})
            active_refs.append(decayed)
        # else: TTL <= 0, reference expires (not added to active_refs)

    # Replace collection contents
    references.clear()
    references.extend(active_refs)

    return len(references) < initial_count


def get_active_references(
    references: "ReferenceCollection"
) -> list[Reference]:
    """
    Filters for references that are still active (not expired).

    Business Rules:
    - Persistent references (TTL = -1) are always active
    - Regular references with TTL > 0 are active
    - References with TTL <= 0 are inactive

    Args:
        references: Reference collection

    Returns:
        List of active references
    """
    return [
        ref for ref in references
        if ref.persistent or ref.ttl > 0
    ]


def get_persistent_references(
    references: "ReferenceCollection"
) -> list[Reference]:
    """
    Filters for persistent references only.

    Args:
        references: Reference collection

    Returns:
        List of persistent references
    """
    return [ref for ref in references if ref.persistent]


def refresh_reference_ttl(
    references: "ReferenceCollection",
    path: str,
    new_ttl: int,
) -> bool:
    """
    Refreshes TTL for a specific reference.

    Business Rules:
    - Can refresh non-persistent references
    - Cannot modify persistent references
    - Reference must exist

    Args:
        references: Reference collection
        path: Path of reference to refresh
        new_ttl: New TTL value

    Returns:
        True if reference was found and refreshed

    Raises:
        ValueError: If trying to refresh persistent reference
    """
    for i, ref in enumerate(references):
        if ref.path == path:
            if ref.persistent:
                raise ValueError(f"Cannot refresh persistent reference: {path}")

            refreshed = ref.model_copy(update={"ttl": new_ttl})
            references[i] = refreshed
            return True

    return False
```

### todos.py - Todo Validation and Filtering

**Key Responsibilities:**

- Validate todo items
- Filter todos by status
- Sort todos by priority
- Validate todo state transitions

```python
from typing import TYPE_CHECKING

from pipe.core.models.todo import TodoItem, TodoStatus

if TYPE_CHECKING:
    pass


def validate_todo(todo: TodoItem) -> bool:
    """
    Validates todo item according to business rules.

    Business Rules:
    - Title must not be empty
    - Status must be valid
    - Completed todos must have completion timestamp

    Args:
        todo: Todo item to validate

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    if not todo.title or not todo.title.strip():
        raise ValueError("Todo title cannot be empty")

    if todo.status not in TodoStatus:
        raise ValueError(f"Invalid todo status: {todo.status}")

    if todo.status == TodoStatus.COMPLETED and not todo.completed_at:
        raise ValueError("Completed todo must have completion timestamp")

    return True


def filter_todos_by_status(
    todos: list[TodoItem],
    status: TodoStatus,
) -> list[TodoItem]:
    """
    Filters todos by status.

    Args:
        todos: List of todos
        status: Status to filter by

    Returns:
        Filtered list of todos
    """
    return [todo for todo in todos if todo.status == status]


def get_active_todos(todos: list[TodoItem]) -> list[TodoItem]:
    """
    Gets all non-completed todos.

    Args:
        todos: List of todos

    Returns:
        List of active todos
    """
    return [
        todo for todo in todos
        if todo.status != TodoStatus.COMPLETED
    ]


def sort_todos_by_priority(todos: list[TodoItem]) -> list[TodoItem]:
    """
    Sorts todos by priority and creation time.

    Business Rules:
    - In-progress todos come first
    - Then not-started todos
    - Within each group, sort by creation time
    - Completed todos come last

    Args:
        todos: List of todos

    Returns:
        Sorted list of todos
    """
    def sort_key(todo: TodoItem) -> tuple:
        # Priority order: in-progress (0), not-started (1), completed (2)
        status_priority = {
            TodoStatus.IN_PROGRESS: 0,
            TodoStatus.NOT_STARTED: 1,
            TodoStatus.COMPLETED: 2,
        }
        return (
            status_priority.get(todo.status, 99),
            todo.created_at or "",
        )

    return sorted(todos, key=sort_key)


def can_transition_status(
    current: TodoStatus,
    new: TodoStatus,
) -> bool:
    """
    Validates if status transition is allowed.

    Business Rules:
    - Can start a not-started todo (not-started -> in-progress)
    - Can complete an in-progress todo (in-progress -> completed)
    - Can complete a not-started todo directly (not-started -> completed)
    - Cannot reopen completed todos

    Args:
        current: Current status
        new: New status

    Returns:
        True if transition is valid
    """
    valid_transitions = {
        TodoStatus.NOT_STARTED: {TodoStatus.IN_PROGRESS, TodoStatus.COMPLETED},
        TodoStatus.IN_PROGRESS: {TodoStatus.COMPLETED, TodoStatus.NOT_STARTED},
        TodoStatus.COMPLETED: set(),  # No transitions from completed
    }

    return new in valid_transitions.get(current, set())
```

### artifacts.py - Artifact Management

```python
from typing import TYPE_CHECKING

from pipe.core.models.artifact import Artifact

if TYPE_CHECKING:
    pass


def validate_artifact_path(path: str, project_root: str) -> bool:
    """
    Validates artifact path according to business rules.

    Business Rules:
    - Path must be relative to project root
    - Path must not escape project root (no ../)
    - Path must not be absolute

    Args:
        path: Artifact path to validate
        project_root: Project root directory

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    if os.path.isabs(path):
        raise ValueError(f"Artifact path must be relative: {path}")

    if ".." in path:
        raise ValueError(f"Artifact path cannot contain '..': {path}")

    # Check that resolved path is within project root
    full_path = os.path.normpath(os.path.join(project_root, path))
    if not full_path.startswith(project_root):
        raise ValueError(f"Artifact path escapes project root: {path}")

    return True


def get_pending_artifacts(artifacts: list[Artifact]) -> list[Artifact]:
    """
    Filters for artifacts that haven't been created yet.

    Args:
        artifacts: List of artifacts

    Returns:
        List of pending artifacts
    """
    return [art for art in artifacts if not art.created]


def mark_artifact_created(artifact: Artifact) -> Artifact:
    """
    Marks artifact as created.

    Args:
        artifact: Artifact to mark

    Returns:
        Updated artifact
    """
    return artifact.model_copy(update={"created": True})
```

## Domain Function Patterns

### Pattern 1: Filter and Transform

```python
def process_entities(
    entities: list[Entity],
    filter_fn: Callable[[Entity], bool],
    transform_fn: Callable[[Entity], Entity],
) -> list[Entity]:
    """
    Generic filter and transform pattern.
    """
    return [
        transform_fn(entity)
        for entity in entities
        if filter_fn(entity)
    ]
```

### Pattern 2: Safe Rebuild

```python
def modify_collection(collection: Collection) -> bool:
    """
    Safely rebuilds collection without mutating during iteration.
    """
    new_items = []
    modified = False

    for item in collection:
        if should_modify(item):
            new_items.append(modify(item))
            modified = True
        else:
            new_items.append(item)

    if modified:
        collection.clear()
        collection.extend(new_items)

    return modified
```

### Pattern 3: Business Rule Validation

```python
def apply_rule(entity: Entity, rule: Rule) -> Entity:
    """
    Applies business rule with validation.
    """
    # Pre-condition check
    if not can_apply_rule(entity, rule):
        raise ValueError(f"Cannot apply rule {rule} to {entity}")

    # Apply transformation
    result = _transform_entity(entity, rule)

    # Post-condition check
    if not is_valid_result(result):
        raise ValueError(f"Rule application resulted in invalid state")

    return result
```

## Testing

### Unit Testing Domain Logic

```python
# tests/core/domains/test_turns.py
from pipe.core.domains.turns import get_turns_for_prompt, expire_old_tool_responses
from pipe.core.models.turn import UserTaskTurn, ToolResponseTurn
from pipe.core.collections.turns import TurnCollection

def test_get_turns_for_prompt_limits_tool_responses():
    # Setup
    turns = TurnCollection([
        UserTaskTurn(message="Task 1", timestamp="2024-01-01T00:00:00"),
        ToolResponseTurn(message="Response 1", timestamp="2024-01-01T00:01:00"),
        ToolResponseTurn(message="Response 2", timestamp="2024-01-01T00:02:00"),
        ToolResponseTurn(message="Response 3", timestamp="2024-01-01T00:03:00"),
        ToolResponseTurn(message="Response 4", timestamp="2024-01-01T00:04:00"),
        UserTaskTurn(message="Task 2", timestamp="2024-01-01T00:05:00"),
    ])

    # Execute
    result = list(get_turns_for_prompt(turns, tool_response_limit=3))

    # Verify
    tool_responses = [t for t in result if isinstance(t, ToolResponseTurn)]
    assert len(tool_responses) == 3  # Only last 3 tool responses


def test_expire_old_tool_responses():
    # Setup with 5 user tasks
    turns = TurnCollection([
        UserTaskTurn(message="Task 1", timestamp="2024-01-01T00:00:00"),
        ToolResponseTurn(message="Old response", timestamp="2024-01-01T00:01:00"),
        UserTaskTurn(message="Task 2", timestamp="2024-01-01T00:02:00"),
        UserTaskTurn(message="Task 3", timestamp="2024-01-01T00:03:00"),
        UserTaskTurn(message="Task 4", timestamp="2024-01-01T00:04:00"),
        ToolResponseTurn(message="Recent response", timestamp="2024-01-01T00:05:00"),
        UserTaskTurn(message="Task 5", timestamp="2024-01-01T00:06:00"),
    ])

    # Execute
    modified = expire_old_tool_responses(turns, expiration_threshold=3)

    # Verify
    assert modified is True
    assert "[expired]" in turns[1].message.lower()
    assert "Recent response" == turns[5].message  # Recent not expired
```

## Best Practices

### 1. Keep Functions Pure

```python
# ✅ GOOD: Pure function
def filter_active(items: list[Item]) -> list[Item]:
    return [item for item in items if item.active]

# ❌ BAD: Side effects
def filter_active(items: list[Item]) -> list[Item]:
    items[:] = [item for item in items if item.active]  # Mutates input
    return items
```

### 2. Explicit Business Rules

```python
# ✅ GOOD: Clear business rules in docstring
def decay_ttl(references: list[Reference]) -> None:
    """
    Business Rules:
    - Persistent references (TTL = -1) are not affected
    - Regular references decrement by 1
    - References with TTL <= 0 are removed
    """
    ...

# ❌ BAD: Implicit rules
def decay_ttl(references: list[Reference]) -> None:
    """Decays TTL."""
    ...
```

### 3. Avoid Services Dependency

```python
# ✅ GOOD: Domain is independent
def process_turn(turn: Turn) -> Turn:
    # Pure business logic
    return turn.model_copy(update={"processed": True})

# ❌ BAD: Depends on service
def process_turn(turn: Turn, service: SessionService) -> Turn:
    # Domain shouldn't depend on service
    service.save_turn(turn)
    return turn
```

## Summary

Domains are the **heart of business logic**:

- ✅ Pure business rules
- ✅ Stateless transformations
- ✅ No side effects
- ✅ Highly testable
- ❌ No I/O operations
- ❌ No external dependencies
- ❌ No persistence

Domains encode the **what** (business rules), while services coordinate the **how** (execution).
