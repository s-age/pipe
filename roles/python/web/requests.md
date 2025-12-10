# Request Models Layer

## Purpose

Request models provide **input validation** for HTTP requests using Pydantic. They ensure data meets requirements before reaching business logic.

**Two patterns supported:**

1. **Body-only** (Legacy): Validate request body only
2. **Unified** (New): Validate path params + body together (Laravel/Struts style)

## Responsibilities

1. **Input Validation** - Validate structure and types
2. **Field Validation** - Apply custom validators
3. **Type Coercion** - Convert string inputs to types
4. **Error Messages** - Clear validation errors
5. **API Documentation** - Self-document inputs

## Rules

### ✅ DO

- Inherit from BaseModel (legacy) or BaseRequest (new)
- Type-hint all fields
- Use Field() for constraints
- Use @field_validator for custom rules
- Provide clear field descriptions

### ❌ DON'T

- **NO business logic** - Only validation
- **NO persistence** - Pure data structures
- **NO service calls** - No side effects
- **NO complex transformations** - Keep simple

## File Structure

```
requests/
├── base_request.py          # Base for unified pattern
├── common.py                # Utilities
└── sessions/
    ├── start_session.py
    ├── fork_session.py
    ├── edit_references.py
    └── ...
```

## Dependencies

**Allowed:**
- ✅ Pydantic
- ✅ Core Models (for nested types)
- ✅ Validators (custom validation)
- ✅ Standard library

**Forbidden:**
- ❌ Services
- ❌ Repositories
- ❌ Actions
- ❌ Controllers

## Example: Body-only (Legacy)

```python
"""Request body model for starting session."""

from pydantic import BaseModel, field_validator

class StartSessionBodyModel(BaseModel):
    """
    Validate start session request body.
    
    Path parameters accessed separately in action.
    """
    
    purpose: str
    agent_name: str | None = None
    model_name: str | None = None
    
    @field_validator("purpose")
    @classmethod
    def purpose_not_empty(cls, v: str) -> str:
        """Validate purpose is not empty."""
        if not v.strip():
            raise ValueError("Purpose cannot be empty")
        return v
```

## Example: Unified (New - Laravel/Struts Style)

```python
"""Unified request model for forking session."""

from pydantic import field_validator
from pipe.web.requests.base_request import BaseRequest

class ForkSessionRequest(BaseRequest):
    """
    Validate fork session request (path + body together).
    
    Validation happens BEFORE action execution.
    Type-safe access to all request data.
    """
    
    # Path parameters (declared at class level)
    path_params = ["session_id"]
    
    # Path param fields
    session_id: str
    
    # Body fields
    fork_index: int
    new_purpose: str | None = None
    
    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Validate session ID format."""
        if not v or len(v) < 10:
            raise ValueError("Invalid session ID")
        return v
    
    @field_validator("fork_index")
    @classmethod
    def validate_fork_index(cls, v: int) -> int:
        """Validate fork index is non-negative."""
        if v < 0:
            raise ValueError("Fork index must be non-negative")
        return v
```

## Common Patterns

### Pattern 1: Required Fields with Constraints

```python
class CreateEntityRequest(BaseRequest):
    path_params = ["project_id"]
    
    project_id: str
    name: str = Field(min_length=1, max_length=100)
    count: int = Field(ge=0, le=1000)
```

### Pattern 2: Optional Fields with Defaults

```python
class UpdateEntityRequest(BaseRequest):
    path_params = ["entity_id"]
    
    entity_id: str
    name: str | None = None
    enabled: bool = True
```

### Pattern 3: Nested Validation

```python
class EditReferencesRequest(BaseRequest):
    path_params = ["session_id"]
    
    session_id: str
    references: list[Reference]  # Nested model
    
    @field_validator("references")
    @classmethod
    def validate_references(cls, v: list[Reference]) -> list[Reference]:
        """Validate references list."""
        if len(v) == 0:
            raise ValueError("At least one reference required")
        return v
```

## Testing

```python
# tests/web/requests/test_fork_session.py

def test_fork_session_request_validates_data():
    """Test request validates valid data."""
    request = ForkSessionRequest(
        session_id="abc123",
        fork_index=5,
        new_purpose="Test fork"
    )
    
    assert request.session_id == "abc123"
    assert request.fork_index == 5

def test_fork_session_request_rejects_negative_index():
    """Test request rejects negative fork_index."""
    with pytest.raises(ValidationError) as exc:
        ForkSessionRequest(
            session_id="abc123",
            fork_index=-1
        )
    
    assert "non-negative" in str(exc.value)

def test_fork_session_request_requires_session_id():
    """Test request requires session_id."""
    with pytest.raises(ValidationError):
        ForkSessionRequest(fork_index=5)
```

## Summary

**Request Models:**
- ✅ Input validation with Pydantic
- ✅ Two patterns: body-only or unified
- ✅ Clear validation errors
- ✅ Type-safe field access
- ❌ No logic, persistence, or side effects

**Request models define valid input shape, not what to do with it**
