# Models Layer

## Purpose

Models are **pure data structures** defined with Pydantic. They represent the core domain entities with strict type safety, validation, and serialization capabilities.

**Architecture Principle: Models define TYPES, Domains define LOGIC**

For every model in `models/`, there should be a corresponding domain module in `domains/`:

```
models/session.py       →  domains/session.py       (fork, destroy)
models/hyperparameters.py →  domains/hyperparameters.py (merge)
models/turn.py          →  domains/turns.py         (filter, expire)
models/reference.py     →  domains/references.py    (TTL management)
```

## Responsibilities

1. **Data Structure Definition** - Define the shape of domain entities
2. **Type Safety** - Enforce type constraints at runtime  
3. **Data Validation** - Ensure data integrity (format, range, type)
4. **Serialization** - Convert between Python objects and JSON/dict
5. **Immutability Contracts** - Define which fields can/cannot be modified

## Rules

### ✅ DO

- Use Pydantic BaseModel for all models
- Type-annotate all fields with precise types
- Use Field() for constraints and documentation
- Use @field_validator for **data validation only** (format, range, type)
- Use ConfigDict for model behavior (frozen, validate_assignment)
- Compose models with other models
- Keep models simple and focused on data structure

### ❌ DON'T

- **NO business logic** - Move to domains/
- **NO methods** (except Pydantic lifecycle methods) - Move to domains/
- **NO file I/O** - Move to repositories/
- **NO external API calls** - Move to agents/
- **NO service dependencies** - Models are the lowest layer
- **NO complex calculations** - Move to domains/
- **NO state transitions** - Move to domains/

## File Structure

```
models/
├── session.py           # Session entity (TYPE only, no fork/destroy)
├── hyperparameters.py   # Hyperparameters (TYPE only, no merge)
├── turn.py              # Turn types (TYPE only)
├── reference.py         # Reference (TYPE only, no TTL logic)
└── ...

domains/                 # Business logic lives here
├── session.py           # fork_session(), destroy_session()
├── hyperparameters.py   # merge_hyperparameters()
├── turns.py             # filter, expire logic
└── references.py        # TTL management, decay
```

## Examples

### Example 1: Simple Value Object

```python
from pydantic import BaseModel, Field

class Hyperparameters(BaseModel):
    """Model hyperparameters - pure data structure."""
    
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1)
```

**Corresponding domain logic:**

```python
# domains/hyperparameters.py
def merge_hyperparameters(
    existing: Hyperparameters | None, 
    new_params: dict
) -> Hyperparameters:
    """Merge logic lives in domains, not models."""
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

### Example 2: Entity with Collections

```python
from pydantic import BaseModel, Field, ConfigDict
from pipe.core.collections.turns import TurnCollection

class Session(BaseModel):
    """Session entity - data structure only."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    session_id: str
    purpose: str
    turns: TurnCollection = Field(default_factory=TurnCollection)
    hyperparameters: Hyperparameters | None = None
```

**Corresponding domain logic:**

```python
# domains/session.py
def fork_session(
    original: Session, 
    fork_index: int, 
    timezone
) -> Session:
    """Complex fork logic lives in domains, not Session model."""
    # Validation
    if not (0 <= fork_index < len(original.turns)):
        raise IndexError(...)
    
    # ID generation (complex business logic)
    new_id = _generate_fork_id(original, fork_index)
    
    # Create forked session
    return Session(
        session_id=new_id,
        purpose=f"Fork of: {original.purpose}",
        turns=TurnCollection(original.turns[:fork_index + 1]),
        ...
    )
```

### Example 3: Data Validation (Allowed in Models)

```python
from pydantic import BaseModel, field_validator

class Reference(BaseModel):
    """File reference with validation."""
    
    path: str
    ttl: int = 5
    
    @field_validator('path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Data validation - checking format, not business rules."""
        if not v or not v.strip():
            raise ValueError("Path cannot be empty")
        return v.strip()
    
    @field_validator('ttl')
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        """Data validation - checking range."""
        if v < -1:
            raise ValueError("TTL must be -1 or >= 0")
        return v
```

**Note:** Complex business validation (e.g., checking if path exists, is within project root) belongs in `domains/references.py`, not here.

## Common Mistakes

### ❌ BAD: Business Logic in Model

```python
class Session(BaseModel):
    session_id: str
    turns: TurnCollection
    
    def fork(self, index: int) -> Session:  # DON'T
        """Complex ID generation, validation - belongs in domains/"""
        new_id = hashlib.sha256(...).hexdigest()
        return Session(session_id=new_id, ...)
    
    def filter_recent_turns(self) -> list[Turn]:  # DON'T
        """Filtering logic - belongs in domains/"""
        return self.turns[-10:]
```

### ✅ GOOD: Pure Data Structure

```python
# models/session.py
class Session(BaseModel):
    """Pure data structure."""
    session_id: str
    turns: TurnCollection

# domains/session.py
def fork_session(original: Session, index: int) -> Session:
    """Business logic in domains."""
    new_id = _generate_fork_id(original, index)
    return Session(session_id=new_id, ...)

def filter_recent_turns(session: Session, limit: int) -> list[Turn]:
    """Filtering logic in domains."""
    return session.turns[-limit:]
```

## Testing

```python
# tests/core/models/test_session.py
def test_session_creation():
    """Test data structure creation and validation."""
    session = Session(
        session_id="test123",
        purpose="Test",
        turns=TurnCollection(),
    )
    assert session.session_id == "test123"

def test_session_validation():
    """Test Pydantic validation."""
    with pytest.raises(ValueError):
        Session(session_id="", purpose="Test")  # Empty ID
```

Domain logic testing belongs in `tests/core/domains/`.

## Summary

**Models:**
- ✅ Pure data structures with Pydantic
- ✅ Type definitions and data validation
- ✅ Serialization support
- ❌ No business logic, no methods, no I/O

**For business logic, see `domains/`**
