# Validators Layer

## Purpose

Validators provide **complex validation logic** beyond simple type checks. They centralize multi-field and cross-entity validation, returning structured validation results.

## Responsibilities

1. **Complex Validation** - Multi-field, cross-entity checks
2. **Business Rule Enforcement** - Validate business constraints
3. **Validation Results** - Return structured error details
4. **Reusable Rules** - Share validation across layers
5. **Clear Errors** - Actionable validation messages

## Rules

### ✅ DO

- Handle complex validation (more than type checks)
- Return structured ValidationResult objects
- Provide clear error messages with field names
- Keep validators stateless (pure functions)
- Reuse validation logic across layers

### ❌ DON'T

- **NO data persistence** - Only validation
- **NO business logic execution** - Only checks
- **NO side effects** - Pure validation only
- **NO service coordination** - Validators don't orchestrate

## File Structure

```
validators/
├── session_validator.py    # Session validation
├── reference_validator.py  # Reference validation
└── turn_validator.py       # Turn validation
```

## Dependencies

**Allowed:**
- ✅ models/ - Type information
- ✅ utils/ - Helper functions
- ✅ Standard library

**Forbidden:**
- ❌ services/ - No orchestration
- ❌ repositories/ - No data access
- ❌ agents/ - No external calls

## Example

```python
"""Validators for Session."""

from typing import List
from pydantic import BaseModel

class ValidationError(BaseModel):
    """Single validation error."""
    field: str
    message: str
    code: str

class ValidationResult(BaseModel):
    """Validation result."""
    is_valid: bool
    errors: List[ValidationError]
    
    @property
    def error_messages(self) -> List[str]:
        return [e.message for e in self.errors]

class SessionValidator:
    """
    Validates Session objects.
    
    Business Rules:
    - Purpose must not be empty
    - Fork index must reference model_response turn
    - References must have valid TTL
    """
    
    @staticmethod
    def validate_fork_point(turns: list, fork_index: int) -> ValidationResult:
        """
        Validate fork point is valid.
        
        Business Rules:
        - Index must be in range
        - Turn at index must be model_response
        
        Args:
            turns: List of turns
            fork_index: Index to fork from
            
        Returns:
            ValidationResult with errors if any
        """
        errors = []
        
        # Check range
        if not (0 <= fork_index < len(turns)):
            errors.append(ValidationError(
                field="fork_index",
                message=f"Index {fork_index} out of range (0-{len(turns)-1})",
                code="INDEX_OUT_OF_RANGE"
            ))
            return ValidationResult(is_valid=False, errors=errors)
        
        # Check turn type
        turn = turns[fork_index]
        if turn.type != "model_response":
            errors.append(ValidationError(
                field="fork_index",
                message=f"Turn at {fork_index} is {turn.type}, must be model_response",
                code="INVALID_FORK_POINT"
            ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    @staticmethod
    def validate_reference_ttl(ttl: int | None) -> ValidationResult:
        """
        Validate reference TTL value.
        
        Business Rules:
        - If set, must be positive
        - Maximum value is 100 turns
        
        Args:
            ttl: TTL value to validate
            
        Returns:
            ValidationResult
        """
        errors = []
        
        if ttl is not None:
            if ttl < 0:
                errors.append(ValidationError(
                    field="ttl",
                    message="TTL must be positive",
                    code="NEGATIVE_TTL"
                ))
            elif ttl > 100:
                errors.append(ValidationError(
                    field="ttl",
                    message="TTL cannot exceed 100 turns",
                    code="TTL_TOO_LARGE"
                ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
```

## Common Patterns

### Pattern 1: Multi-Field Validation

```python
@staticmethod
def validate_entity(entity: Model) -> ValidationResult:
    """Validate multiple fields together."""
    errors = []
    
    if entity.field1 and not entity.field2:
        errors.append(ValidationError(
            field="field2",
            message="field2 required when field1 is set",
            code="MISSING_REQUIRED_FIELD"
        ))
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

### Pattern 2: Cross-Entity Validation

```python
@staticmethod
def validate_consistency(entity1: Model1, entity2: Model2) -> ValidationResult:
    """Validate consistency between entities."""
    errors = []
    
    if entity1.ref_id != entity2.id:
        errors.append(ValidationError(
            field="ref_id",
            message="Reference ID mismatch",
            code="REF_MISMATCH"
        ))
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

## Testing

```python
# tests/core/validators/test_session_validator.py

def test_validate_fork_point_accepts_valid_index():
    """Test validation passes for valid fork point."""
    turns = [
        Turn(type="model_response", content="response1"),
        Turn(type="user_input", content="input1"),
    ]
    
    result = SessionValidator.validate_fork_point(turns, 0)
    
    assert result.is_valid
    assert len(result.errors) == 0

def test_validate_fork_point_rejects_invalid_type():
    """Test validation fails for non-model_response turn."""
    turns = [Turn(type="user_input", content="input1")]
    
    result = SessionValidator.validate_fork_point(turns, 0)
    
    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].code == "INVALID_FORK_POINT"

def test_validate_fork_point_rejects_out_of_range():
    """Test validation fails for out of range index."""
    turns = [Turn(type="model_response", content="response1")]
    
    result = SessionValidator.validate_fork_point(turns, 5)
    
    assert not result.is_valid
    assert result.errors[0].code == "INDEX_OUT_OF_RANGE"
```

## Summary

**Validators:**
- ✅ Complex validation logic
- ✅ Structured ValidationResult objects
- ✅ Clear error messages
- ✅ Stateless and reusable
- ❌ No persistence, side effects, or orchestration

**Validators answer "is this valid?", not "how do I fix it?"**
