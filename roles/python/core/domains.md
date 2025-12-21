# Domains Layer

## Purpose

Domains contain **pure business logic** for manipulating core data entities. This layer implements the rules and behaviors that define how the system works, isolated from infrastructure concerns.

**Architecture Principle: 1:1 Correspondence with Models**

For every model in `models/`, there should be a corresponding domain module in `domains/`:

```
models/session.py       →  domains/session.py       (fork, destroy)
models/hyperparameters.py →  domains/hyperparameters.py (merge)
models/turn.py          →  domains/turns.py         (filter, expire, delete)
models/reference.py     →  domains/references.py    (TTL decay, filtering)
```

**Why this pattern?**

1. **Separation of Concerns**: Models define WHAT data looks like (types), Domains define HOW to work with it (logic)
2. **Testability**: Pure functions in domains are easier to test than methods in Pydantic models
3. **Pydantic-Friendly**: Avoids complex logic in Pydantic models which can interfere with serialization
4. **Clear Organization**: Easy to find where logic lives - just look for the corresponding domain module

## Responsibilities

1. **Business Rules** - Implement domain-specific rules and constraints
2. **Complex Operations** - Operations too complex for models (e.g., fork with ID generation)
3. **Data Transformations** - Transform and filter data according to business logic
4. **State Transitions** - Define valid state changes
5. **Calculations** - Business calculations and derivations

## Rules

### ✅ DO

- Write pure functions (input → output, no side effects)
- Implement business rules and validations
- Transform and filter data
- Work with models and collections as parameters
- Use TYPE_CHECKING imports to avoid circular dependencies
- Keep functions stateless
- Document business rules clearly in docstrings

### ❌ DON'T

- **NO file I/O** - Domains are pure, move I/O to repositories/
- **NO API calls** - No external system interactions
- **NO persistence** - Don't save data, just transform it
- **NO service dependencies** - Domains are called BY services, not the reverse
- **NO global state** - Functions should be stateless
- **NO side effects** - Functions should not modify external state

## File Structure

```
domains/
├── session.py           # fork_session(), destroy_session()
├── hyperparameters.py   # merge_hyperparameters()
├── turns.py             # filter, expire, delete logic
├── references.py        # TTL decay, filtering
└── ...

models/                  # Corresponding type definitions
├── session.py
├── hyperparameters.py
├── turn.py
├── reference.py
└── ...
```

## Examples

### Example 1: Complex Operation (Session Fork)

```python
"""Domain logic for Session."""

import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipe.core.models.session import Session

def fork_session(
    original: "Session", 
    fork_index: int, 
    timezone
) -> "Session":
    """
    Creates a forked session with new ID generation.
    
    Business Rules:
    - Fork index must be within range
    - Fork point must be a model_response turn
    - New ID is SHA256 hash of (purpose + original_id + fork_index + timestamp)
    - Forked session contains history up to fork point
    
    Args:
        original: Original session to fork
        fork_index: Turn index to fork from
        timezone: Timezone for timestamp
        
    Returns:
        New forked session
        
    Raises:
        IndexError: If fork_index out of range
        ValueError: If fork point is not model_response
    """
    from pipe.core.models.session import Session
    
    # Validate range
    if not (0 <= fork_index < len(original.turns)):
        raise IndexError(f"fork_index {fork_index} out of range")
    
    # Validate turn type
    if original.turns[fork_index].type != "model_response":
        raise ValueError("Can only fork from model_response turn")
    
    # Generate new ID (complex business logic)
    identity = json.dumps({
        "purpose": f"Fork of: {original.purpose}",
        "original_id": original.session_id,
        "fork_at_turn": fork_index,
        "timestamp": get_current_timestamp(timezone),
    }, sort_keys=True)
    new_id = hashlib.sha256(identity.encode()).hexdigest()
    
    # Create forked session
    return Session(
        session_id=new_id,
        purpose=f"Fork of: {original.purpose}",
        turns=original.turns[:fork_index + 1],
        ...
    )
```

### Example 2: Data Transformation (Hyperparameter Merge)

```python
"""Domain logic for Hyperparameters."""

from typing import Any
from pipe.core.models.hyperparameters import Hyperparameters

def merge_hyperparameters(
    existing: Hyperparameters | None, 
    new_params: dict[str, Any]
) -> Hyperparameters:
    """
    Merge new hyperparameter values with existing ones.
    
    Business Rules:
    - If no existing, use new values directly
    - If existing, merge new with defaults from existing
    - Unspecified parameters retain existing values
    
    Args:
        existing: Current hyperparameters or None
        new_params: New parameter values (partial updates allowed)
        
    Returns:
        Merged Hyperparameters instance
    """
    if existing:
        merged = {
            "temperature": new_params.get("temperature", existing.temperature),
            "top_p": new_params.get("top_p", existing.top_p),
            "top_k": new_params.get("top_k", existing.top_k),
        }
    else:
        merged = new_params
    
    return Hyperparameters(**merged)
```

### Example 3: Filtering (Turn History)

```python
"""Domain logic for Turns."""

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from pipe.core.models.turn import Turn
    from pipe.core.collections.turns import TurnCollection

def get_turns_for_prompt(
    turns: "TurnCollection", 
    tool_response_limit: int = 3
) -> Iterator["Turn"]:
    """
    Filter turns for prompt generation.
    
    Business Rules:
    - Exclude last turn (current task)
    - Include only last N tool responses to prevent context bloat
    - Preserve all other turns
    
    Args:
        turns: Full turn collection
        tool_response_limit: Max tool responses to include
        
    Yields:
        Turns suitable for prompt context
    """
    tool_response_count = 0
    history = turns[:-1]  # Exclude last
    
    for turn in reversed(history):
        if turn.type == "tool_response":
            tool_response_count += 1
            if tool_response_count > tool_response_limit:
                continue  # Skip old tool responses
        yield turn
```

## Common Patterns

### Pattern 1: Pure Transformation

```python
def transform(input_data: Model) -> Model:
    """Pure function: input → output, no side effects."""
    # Business logic
    return modified_model
```

### Pattern 2: Safe Rebuild (for collections)

```python
def process_collection(items: Collection) -> bool:
    """Rebuild collection safely without mutating during iteration."""
    new_items = []
    modified = False
    
    for item in items:
        if should_modify(item):
            new_items.append(modify(item))
            modified = True
        else:
            new_items.append(item)
    
    if modified:
        items.clear()
        items.extend(new_items)
    
    return modified
```

### Pattern 3: Business Rule Validation

```python
def apply_rule(entity: Model, param: str) -> Model:
    """Apply business rule with pre/post validation."""
    # Pre-condition
    if not can_apply(entity, param):
        raise ValueError("Cannot apply rule")
    
    # Transform
    result = _transform(entity, param)
    
    # Post-condition
    if not is_valid(result):
        raise ValueError("Invalid result")
    
    return result
```

## Testing

```python
# tests/core/domains/test_session.py

def test_fork_session_validates_index():
    """Test fork validates index range."""
    session = create_test_session()
    
    with pytest.raises(IndexError):
        fork_session(session, 999, timezone)

def test_fork_session_generates_unique_id():
    """Test fork generates unique session ID."""
    session = create_test_session()
    
    forked = fork_session(session, 0, timezone)
    
    assert forked.session_id != session.session_id
    assert len(forked.session_id) == 64  # SHA256 hex

def test_merge_hyperparameters_preserves_unspecified():
    """Test merge preserves unspecified parameters."""
    existing = Hyperparameters(temperature=0.8, top_p=0.9, top_k=40)
    
    merged = merge_hyperparameters(existing, {"temperature": 1.0})
    
    assert merged.temperature == 1.0
    assert merged.top_p == 0.9  # Preserved
    assert merged.top_k == 40   # Preserved
```

## Summary

**Domains:**
- ✅ Pure business logic functions
- ✅ Stateless transformations
- ✅ Work with models as parameters
- ✅ 1:1 correspondence with models
- ❌ No I/O, no persistence, no side effects
- ❌ No service dependencies

**Domains define HOW to work with data, Models define WHAT data looks like**
