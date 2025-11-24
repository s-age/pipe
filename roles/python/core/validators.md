# Validators Layer

## Purpose

Validators provide **complex validation logic and business rule enforcement**. They centralize validation that's too complex for simple Pydantic validators and coordinate multi-field or cross-entity validation.

## Responsibilities

1. **Complex Validation** - Multi-field, cross-entity validation
2. **Business Rules** - Enforce business constraints
3. **Validation Results** - Return detailed validation results
4. **Reusable Rules** - Share validation logic across layers
5. **Clear Error Messages** - Provide actionable validation feedback

## Characteristics

- ✅ Complex validation logic (more than simple type checks)
- ✅ Business rule enforcement
- ✅ Clear validation result objects
- ✅ Reusable across layers
- ✅ Type-safe validation logic
- ❌ **NO data persistence** - only validation
- ❌ **NO business logic execution** - only checks
- ❌ **NO side effects** - pure validation

## File Structure

```
validators/
├── __init__.py
├── session_validator.py    # Session validation
├── reference_validator.py  # Reference validation
└── turn_validator.py       # Turn validation
```

## Dependencies

**Allowed:**

- ✅ Models (for type information)
- ✅ Utils (for helper functions)
- ✅ Standard library

**Forbidden:**

- ❌ Services (validators are pure, no orchestration)
- ❌ Repositories (no data access)
- ❌ Agents (no external API calls)
- ❌ Domains (use validators FROM domains, not the reverse)

## Template

```python
"""
Validators for [entity].

Provides complex validation logic for [entity] objects.
"""

from typing import List
from pydantic import BaseModel


class ValidationError(BaseModel):
    """
    Single validation error.

    Attributes:
        field: Field that failed validation
        message: Human-readable error message
        code: Error code for programmatic handling
    """
    field: str
    message: str
    code: str


class ValidationResult(BaseModel):
    """
    Result of validation operation.

    Attributes:
        is_valid: Whether validation passed
        errors: List of validation errors (empty if valid)
    """
    is_valid: bool
    errors: List[ValidationError]

    @property
    def error_messages(self) -> List[str]:
        """Get all error messages."""
        return [error.message for error in self.errors]


class EntityValidator:
    """
    Validator for [entity] objects.

    Provides complex validation logic that goes beyond simple
    field validation in Pydantic models.
    """

    def validate(self, entity: EntityModel) -> ValidationResult:
        """
        Validates entity.

        Args:
            entity: Entity to validate

        Returns:
            ValidationResult with errors if invalid

        Examples:
            validator = EntityValidator()
            result = validator.validate(entity)

            if not result.is_valid:
                for error in result.errors:
                    print(f"{error.field}: {error.message}")
        """
        errors = []

        # Validation logic
        if not self._check_rule_1(entity):
            errors.append(ValidationError(
                field="field1",
                message="Field1 is invalid",
                code="INVALID_FIELD1",
            ))

        if not self._check_rule_2(entity):
            errors.append(ValidationError(
                field="field2",
                message="Field2 is invalid",
                code="INVALID_FIELD2",
            ))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
        )

    def _check_rule_1(self, entity: EntityModel) -> bool:
        """Check business rule 1."""
        return True  # Validation logic

    def _check_rule_2(self, entity: EntityModel) -> bool:
        """Check business rule 2."""
        return True  # Validation logic
```

## Real Examples

### session_validator.py - Session Validation

**Key Validations:**

- Session state consistency
- Turn ordering
- Reference integrity
- Hyperparameter validity

```python
"""
Validators for Session objects.

Provides complex validation logic for sessions, turns, and references.
"""

from typing import List, Set
from pydantic import BaseModel

from pipe.core.models.session import Session, Turn, Reference


class ValidationError(BaseModel):
    """
    Single validation error.

    Attributes:
        field: Field that failed validation
        message: Human-readable error message
        code: Error code for programmatic handling
    """
    field: str
    message: str
    code: str


class ValidationResult(BaseModel):
    """
    Result of validation operation.

    Attributes:
        is_valid: Whether validation passed
        errors: List of validation errors
    """
    is_valid: bool
    errors: List[ValidationError]

    @property
    def error_messages(self) -> List[str]:
        """Get all error messages."""
        return [error.message for error in self.errors]


class SessionValidator:
    """
    Validator for Session objects.

    Validates:
    - Session state consistency
    - Turn ordering and completeness
    - Reference integrity
    - Hyperparameter constraints
    """

    def validate(self, session: Session) -> ValidationResult:
        """
        Validates session.

        Performs comprehensive validation including:
        - Turn ordering (sequential turn numbers)
        - Reference integrity (paths exist)
        - Hyperparameter validity
        - Session metadata consistency

        Args:
            session: Session to validate

        Returns:
            ValidationResult with errors if invalid

        Examples:
            validator = SessionValidator()
            result = validator.validate(session)

            if not result.is_valid:
                print("Session validation failed:")
                for error in result.errors:
                    print(f"  {error.field}: {error.message}")
        """
        errors = []

        # Validate turns
        turn_errors = self._validate_turns(session.turns)
        errors.extend(turn_errors)

        # Validate references
        ref_errors = self._validate_references(session.references)
        errors.extend(ref_errors)

        # Validate hyperparameters
        if session.hyperparameters:
            hp_errors = self._validate_hyperparameters(session.hyperparameters)
            errors.extend(hp_errors)

        # Validate session metadata
        meta_errors = self._validate_metadata(session)
        errors.extend(meta_errors)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
        )

    def _validate_turns(self, turns: List[Turn]) -> List[ValidationError]:
        """
        Validates turn list.

        Checks:
        - Turn numbers are sequential (1, 2, 3, ...)
        - No duplicate turn numbers
        - Each turn has required fields
        """
        errors = []

        if not turns:
            # Empty turn list is valid (new session)
            return errors

        # Check sequential turn numbers
        turn_numbers = [turn.turn_number for turn in turns]
        expected_numbers = list(range(1, len(turns) + 1))

        if turn_numbers != expected_numbers:
            errors.append(ValidationError(
                field="turns",
                message=f"Turn numbers must be sequential. Expected {expected_numbers}, got {turn_numbers}",
                code="INVALID_TURN_ORDER",
            ))

        # Check for duplicate turn numbers
        seen_numbers: Set[int] = set()
        for turn in turns:
            if turn.turn_number in seen_numbers:
                errors.append(ValidationError(
                    field="turns",
                    message=f"Duplicate turn number: {turn.turn_number}",
                    code="DUPLICATE_TURN_NUMBER",
                ))
            seen_numbers.add(turn.turn_number)

        # Validate individual turns
        for turn in turns:
            turn_errors = self._validate_turn(turn)
            errors.extend(turn_errors)

        return errors

    def _validate_turn(self, turn: Turn) -> List[ValidationError]:
        """
        Validates individual turn.

        Checks:
        - Turn has required user instruction
        - Turn number is positive
        - Timestamps are valid
        """
        errors = []

        # Check turn number
        if turn.turn_number <= 0:
            errors.append(ValidationError(
                field=f"turns[{turn.turn_number}].turn_number",
                message="Turn number must be positive",
                code="INVALID_TURN_NUMBER",
            ))

        # Check user instruction
        if not turn.user_instruction or not turn.user_instruction.strip():
            errors.append(ValidationError(
                field=f"turns[{turn.turn_number}].user_instruction",
                message="Turn must have user instruction",
                code="MISSING_USER_INSTRUCTION",
            ))

        return errors

    def _validate_references(
        self,
        references: List[Reference],
    ) -> List[ValidationError]:
        """
        Validates reference list.

        Checks:
        - No duplicate paths
        - Valid TTL values
        - Valid purpose values
        """
        errors = []

        # Check for duplicate paths
        seen_paths: Set[str] = set()
        for ref in references:
            if ref.path in seen_paths:
                errors.append(ValidationError(
                    field="references",
                    message=f"Duplicate reference path: {ref.path}",
                    code="DUPLICATE_REFERENCE_PATH",
                ))
            seen_paths.add(ref.path)

        # Validate individual references
        for ref in references:
            ref_errors = self._validate_reference(ref)
            errors.extend(ref_errors)

        return errors

    def _validate_reference(self, reference: Reference) -> List[ValidationError]:
        """
        Validates individual reference.

        Checks:
        - TTL is non-negative
        - Purpose is not empty
        """
        errors = []

        # Check TTL
        if reference.ttl < 0:
            errors.append(ValidationError(
                field=f"references[{reference.path}].ttl",
                message=f"TTL must be non-negative, got {reference.ttl}",
                code="INVALID_REFERENCE_TTL",
            ))

        # Check purpose
        if not reference.purpose or not reference.purpose.strip():
            errors.append(ValidationError(
                field=f"references[{reference.path}].purpose",
                message="Reference must have purpose",
                code="MISSING_REFERENCE_PURPOSE",
            ))

        return errors

    def _validate_hyperparameters(
        self,
        hyperparameters: dict,
    ) -> List[ValidationError]:
        """
        Validates hyperparameters.

        Checks:
        - Temperature is in valid range [0, 2]
        - Top_p is in valid range [0, 1]
        - Max_tokens is positive
        """
        errors = []

        # Check temperature
        temp = hyperparameters.get("temperature")
        if temp is not None:
            if not isinstance(temp, (int, float)):
                errors.append(ValidationError(
                    field="hyperparameters.temperature",
                    message="Temperature must be a number",
                    code="INVALID_TEMPERATURE_TYPE",
                ))
            elif not (0 <= temp <= 2):
                errors.append(ValidationError(
                    field="hyperparameters.temperature",
                    message=f"Temperature must be in range [0, 2], got {temp}",
                    code="INVALID_TEMPERATURE_RANGE",
                ))

        # Check top_p
        top_p = hyperparameters.get("top_p")
        if top_p is not None:
            if not isinstance(top_p, (int, float)):
                errors.append(ValidationError(
                    field="hyperparameters.top_p",
                    message="Top_p must be a number",
                    code="INVALID_TOP_P_TYPE",
                ))
            elif not (0 <= top_p <= 1):
                errors.append(ValidationError(
                    field="hyperparameters.top_p",
                    message=f"Top_p must be in range [0, 1], got {top_p}",
                    code="INVALID_TOP_P_RANGE",
                ))

        # Check max_tokens
        max_tokens = hyperparameters.get("max_tokens")
        if max_tokens is not None:
            if not isinstance(max_tokens, int):
                errors.append(ValidationError(
                    field="hyperparameters.max_tokens",
                    message="Max_tokens must be an integer",
                    code="INVALID_MAX_TOKENS_TYPE",
                ))
            elif max_tokens <= 0:
                errors.append(ValidationError(
                    field="hyperparameters.max_tokens",
                    message=f"Max_tokens must be positive, got {max_tokens}",
                    code="INVALID_MAX_TOKENS_VALUE",
                ))

        return errors

    def _validate_metadata(self, session: Session) -> List[ValidationError]:
        """
        Validates session metadata.

        Checks:
        - Session has ID
        - Session has created timestamp
        """
        errors = []

        # Check session ID
        if not session.session_id or not session.session_id.strip():
            errors.append(ValidationError(
                field="session_id",
                message="Session must have ID",
                code="MISSING_SESSION_ID",
            ))

        # Check created_at
        if not session.created_at:
            errors.append(ValidationError(
                field="created_at",
                message="Session must have created_at timestamp",
                code="MISSING_CREATED_AT",
            ))

        return errors


def validate_session(session: Session) -> ValidationResult:
    """
    Convenience function for session validation.

    Args:
        session: Session to validate

    Returns:
        ValidationResult

    Examples:
        result = validate_session(session)

        if not result.is_valid:
            raise ValueError(f"Invalid session: {result.error_messages}")
    """
    validator = SessionValidator()
    return validator.validate(session)
```

## Validation Patterns

### Pattern 1: ValidationResult Object

```python
class ValidationResult(BaseModel):
    """
    Standard validation result.

    Always returns this from validators for consistency.
    """
    is_valid: bool
    errors: List[ValidationError]

    @property
    def error_messages(self) -> List[str]:
        """Get all error messages."""
        return [error.message for error in self.errors]


# Usage
result = validator.validate(entity)
if not result.is_valid:
    # Handle errors
    for error in result.errors:
        log.error(f"{error.field}: {error.message}")
```

### Pattern 2: Error Codes for Programmatic Handling

```python
class ValidationError(BaseModel):
    """
    Validation error with code.

    Code allows programmatic error handling.
    """
    field: str
    message: str
    code: str  # e.g., "INVALID_TEMPERATURE_RANGE"


# Usage
result = validator.validate(entity)
for error in result.errors:
    if error.code == "INVALID_TEMPERATURE_RANGE":
        # Handle specific error type
        fix_temperature(entity)
```

### Pattern 3: Composite Validation

```python
def validate(self, entity: Entity) -> ValidationResult:
    """
    Composite validation - run multiple checks.
    """
    errors = []

    # Run multiple validation checks
    errors.extend(self._validate_field_a(entity))
    errors.extend(self._validate_field_b(entity))
    errors.extend(self._validate_relationships(entity))

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
    )
```

## Testing

### Unit Testing Validators

```python
# tests/core/validators/test_session_validator.py
import pytest
from pipe.core.models.session import Session, Turn, Reference
from pipe.core.validators.session_validator import (
    SessionValidator,
    validate_session,
)


def test_validate_valid_session():
    session = Session(
        session_id="test-session",
        created_at="2024-01-15T10:00:00+00:00",
        turns=[
            Turn(
                turn_number=1,
                user_instruction="Test instruction",
                created_at="2024-01-15T10:00:00+00:00",
            ),
        ],
        references=[],
        hyperparameters={"temperature": 1.0},
    )

    result = validate_session(session)

    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validate_invalid_turn_order():
    session = Session(
        session_id="test-session",
        created_at="2024-01-15T10:00:00+00:00",
        turns=[
            Turn(
                turn_number=2,  # Should be 1
                user_instruction="Test",
                created_at="2024-01-15T10:00:00+00:00",
            ),
        ],
        references=[],
    )

    result = validate_session(session)

    assert result.is_valid is False
    assert any(e.code == "INVALID_TURN_ORDER" for e in result.errors)


def test_validate_duplicate_turn_number():
    session = Session(
        session_id="test-session",
        created_at="2024-01-15T10:00:00+00:00",
        turns=[
            Turn(
                turn_number=1,
                user_instruction="Test 1",
                created_at="2024-01-15T10:00:00+00:00",
            ),
            Turn(
                turn_number=1,  # Duplicate
                user_instruction="Test 2",
                created_at="2024-01-15T10:00:00+00:00",
            ),
        ],
        references=[],
    )

    result = validate_session(session)

    assert result.is_valid is False
    assert any(e.code == "DUPLICATE_TURN_NUMBER" for e in result.errors)


def test_validate_invalid_temperature():
    session = Session(
        session_id="test-session",
        created_at="2024-01-15T10:00:00+00:00",
        turns=[],
        references=[],
        hyperparameters={"temperature": 3.0},  # Out of range
    )

    result = validate_session(session)

    assert result.is_valid is False
    assert any(
        e.code == "INVALID_TEMPERATURE_RANGE"
        for e in result.errors
    )


def test_validate_missing_session_id():
    session = Session(
        session_id="",  # Empty
        created_at="2024-01-15T10:00:00+00:00",
        turns=[],
        references=[],
    )

    result = validate_session(session)

    assert result.is_valid is False
    assert any(e.code == "MISSING_SESSION_ID" for e in result.errors)


def test_validate_duplicate_reference_path():
    session = Session(
        session_id="test-session",
        created_at="2024-01-15T10:00:00+00:00",
        turns=[],
        references=[
            Reference(
                path="test.py",
                purpose="Test",
                added_at="2024-01-15T10:00:00+00:00",
                ttl=5,
            ),
            Reference(
                path="test.py",  # Duplicate
                purpose="Test 2",
                added_at="2024-01-15T10:00:00+00:00",
                ttl=5,
            ),
        ],
    )

    result = validate_session(session)

    assert result.is_valid is False
    assert any(
        e.code == "DUPLICATE_REFERENCE_PATH"
        for e in result.errors
    )
```

## Integration with Other Layers

### Usage in Services

```python
# In service
from pipe.core.validators.session_validator import validate_session

class SessionService:
    def save_session(self, session: Session) -> None:
        # Validate before saving
        result = validate_session(session)

        if not result.is_valid:
            error_msg = ", ".join(result.error_messages)
            raise ValueError(f"Invalid session: {error_msg}")

        # Save to repository
        self.repository.save(session)
```

### Usage in Domains

```python
# In domain
from pipe.core.validators.session_validator import validate_session

def process_session(session: Session) -> Session:
    # Validate session state
    result = validate_session(session)

    if not result.is_valid:
        log.warning(f"Session validation issues: {result.error_messages}")

    # Process session
    ...
```

## Best Practices

### 1. Return ValidationResult, Not Exceptions

```python
# ✅ GOOD: Return result
def validate(self, entity: Entity) -> ValidationResult:
    errors = []
    # Collect all errors
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)

# ❌ BAD: Raise exception
def validate(self, entity: Entity) -> None:
    if not valid:
        raise ValidationError("Invalid")  # Can't collect multiple errors
```

### 2. Collect All Errors, Not Just First

```python
# ✅ GOOD: Collect all errors
def validate(self, entity: Entity) -> ValidationResult:
    errors = []

    # Check all validations
    errors.extend(self._validate_a(entity))
    errors.extend(self._validate_b(entity))
    errors.extend(self._validate_c(entity))

    return ValidationResult(is_valid=len(errors) == 0, errors=errors)

# ❌ BAD: Stop at first error
def validate(self, entity: Entity) -> ValidationResult:
    if not self._validate_a(entity):
        return ValidationResult(is_valid=False, errors=[...])
    # Never gets to check b and c
```

### 3. Provide Clear Error Messages

```python
# ✅ GOOD: Specific, actionable message
ValidationError(
    field="hyperparameters.temperature",
    message="Temperature must be in range [0, 2], got 3.0",
    code="INVALID_TEMPERATURE_RANGE",
)

# ❌ BAD: Vague message
ValidationError(
    field="hyperparameters",
    message="Invalid",
    code="ERROR",
)
```

### 4. Use Error Codes for Programmatic Handling

```python
# ✅ GOOD: Error codes enable automated handling
class ValidationError(BaseModel):
    field: str
    message: str
    code: str  # "INVALID_TEMPERATURE_RANGE"

# Usage
if error.code == "INVALID_TEMPERATURE_RANGE":
    fix_temperature(entity)
```

## Summary

Validators are the **business rule enforcers**:

- ✅ Complex validation logic
- ✅ Business rule enforcement
- ✅ Clear ValidationResult objects
- ✅ Reusable across layers
- ✅ Comprehensive error reporting
- ❌ No data persistence
- ❌ No business logic execution
- ❌ No side effects

Validators ensure data integrity without modifying state.
