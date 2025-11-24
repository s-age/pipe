# Request Models Layer

## Purpose

Request models provide **input validation and parsing** for HTTP requests using Pydantic. They ensure all incoming data meets requirements before reaching business logic.

## Responsibilities

1. **Input Validation** - Validate request data structure and types
2. **Field Validation** - Apply custom validators to fields
3. **Type Coercion** - Convert string inputs to appropriate types
4. **Error Messages** - Provide clear validation error messages
5. **Documentation** - Self-document API input requirements

## Characteristics

- ✅ Pydantic BaseModel subclasses
- ✅ Field validators for custom rules
- ✅ Type hints for all fields
- ✅ Optional fields with defaults
- ✅ Clear validation error messages
- ❌ **NO business logic** - only validation
- ❌ **NO persistence** - pure data structures
- ❌ **NO service calls** - no side effects

## File Structure

```
requests/
├── __init__.py
└── sessions/
    ├── __init__.py
    ├── start_session.py
    ├── send_instruction.py
    ├── fork_session.py
    ├── edit_references.py
    ├── edit_reference_persist.py
    ├── edit_reference_ttl.py
    ├── edit_hyperparameters.py
    ├── edit_session_meta.py
    ├── edit_todos.py
    └── edit_turn.py
```

## Dependencies

**Allowed:**

- ✅ Pydantic (for BaseModel)
- ✅ Core Models (for nested types like Reference)
- ✅ Validators (custom validation functions)
- ✅ Standard library (os, etc. for path validation)

**Forbidden:**

- ❌ Services (no business logic calls)
- ❌ Repositories (no data access)
- ❌ Actions (no action calls)
- ❌ Controllers (no controller calls)

## Template

```python
"""
Pydantic model for validating [operation] request body.
"""

from typing import Any
from pydantic import BaseModel, field_validator


class OperationRequest(BaseModel):
    """
    Request model for [operation] operation.

    Validates all input data for the operation and provides
    clear error messages on validation failure.

    Attributes:
        field1: Description of field1
        field2: Description of field2
        optional_field: Optional field description

    Examples:
        # Valid request
        request = OperationRequest(
            field1="value1",
            field2="value2",
        )

        # Invalid request raises ValidationError
        request = OperationRequest(
            field1="",  # Empty - fails validation
            field2="value2",
        )
    """

    # Required fields
    field1: str
    field2: str

    # Optional fields with defaults
    optional_field: str | None = None

    @field_validator("field1")
    @classmethod
    def validate_field1(cls, v: str) -> str:
        """
        Validate field1.

        Args:
            v: Field value to validate

        Returns:
            Validated value

        Raises:
            ValueError: If validation fails
        """
        if not v or not v.strip():
            raise ValueError("field1 must not be empty")

        return v

    @field_validator("field2")
    @classmethod
    def validate_field2(cls, v: str) -> str:
        """Validate field2."""
        # Custom validation logic
        if len(v) < 3:
            raise ValueError("field2 must be at least 3 characters")

        return v
```

## Real Examples

### start_session.py - Session Creation Request

```python
"""
Pydantic model for validating the request body of the new session API endpoint.
"""

import os
from typing import Any

from pipe.core.models.reference import Reference
from pipe.web.validators.rules.file_exists import validate_list_of_files_exist
from pydantic import BaseModel, field_validator


class StartSessionRequest(BaseModel):
    """
    Request model for starting a new session.

    Validates all required fields for session creation including:
    - Purpose and background (required, non-empty)
    - Initial instruction (required, non-empty)
    - Optional roles (must be valid file paths)
    - Optional references (must be valid file paths)
    - Optional procedure (must be valid file path)
    - Optional hyperparameters

    Attributes:
        purpose: Purpose of the session (required)
        background: Background context (required)
        instruction: Initial instruction to execute (required)
        roles: List of role file paths (optional)
        parent: Parent session ID for forking (optional)
        references: List of file references (optional)
        artifacts: List of artifact paths (optional)
        procedure: Procedure file path (optional)
        multi_step_reasoning_enabled: Enable multi-step reasoning (default: False)
        hyperparameters: AI hyperparameters (optional)

    Examples:
        # Minimal request
        request = StartSessionRequest(
            purpose="Build feature",
            background="Working on API",
            instruction="Create endpoint",
        )

        # Full request with options
        request = StartSessionRequest(
            purpose="Build feature",
            background="Working on API",
            instruction="Create endpoint",
            roles=["roles/python/services.md"],
            references=[
                Reference(
                    path="src/service.py",
                    purpose="Existing service",
                    ttl=5,
                )
            ],
            multi_step_reasoning_enabled=True,
            hyperparameters={"temperature": 0.7},
        )
    """

    # Required fields
    purpose: str
    background: str
    instruction: str

    # Optional fields
    roles: list[str] | None = None
    parent: str | None = None
    references: list[Reference] | None = None
    artifacts: list[str] | None = None
    procedure: str | None = None
    multi_step_reasoning_enabled: bool = False
    hyperparameters: dict[str, Any] | None = None

    @field_validator("purpose", "background", "instruction")
    @classmethod
    def check_not_empty(cls, v: str, field) -> str:
        """
        Validate that required string fields are not empty.

        Args:
            v: Field value
            field: Field info

        Returns:
            Validated value

        Raises:
            ValueError: If field is empty or whitespace-only
        """
        if not v or not v.strip():
            raise ValueError(f"{field.field_name} must not be empty.")
        return v

    @field_validator("roles")
    @classmethod
    def validate_list_of_strings_exist(cls, v: list[str]) -> list[str]:
        """
        Validate that all role files exist.

        Args:
            v: List of role file paths

        Returns:
            Validated list

        Raises:
            ValueError: If any file doesn't exist
        """
        validate_list_of_files_exist(v)
        return v

    @field_validator("references")
    @classmethod
    def validate_list_of_references_exist(cls, v: list[Reference]) -> list[Reference]:
        """
        Validate that all referenced files exist.

        Args:
            v: List of references

        Returns:
            Validated list

        Raises:
            ValueError: If any referenced file doesn't exist
        """
        validate_list_of_files_exist([ref.path for ref in v])
        return v

    @field_validator("procedure")
    @classmethod
    def validate_procedure_exists(cls, v: str) -> str:
        """
        Validate that procedure file exists.

        Args:
            v: Procedure file path

        Returns:
            Validated path

        Raises:
            ValueError: If file doesn't exist
        """
        if v and not os.path.isfile(v):
            raise ValueError(f"File not found: '{v}'")
        return v
```

### edit_references.py - Reference Update Request

```python
"""
Pydantic model for validating reference edit requests.
"""

from pipe.core.models.reference import Reference
from pydantic import BaseModel


class EditReferencesRequest(BaseModel):
    """
    Request model for updating session references.

    Replaces entire reference list for a session.

    Attributes:
        references: New list of references

    Examples:
        request = EditReferencesRequest(
            references=[
                Reference(
                    path="src/file1.py",
                    purpose="First file",
                    ttl=5,
                ),
                Reference(
                    path="src/file2.py",
                    purpose="Second file",
                    ttl=3,
                    persist=True,
                ),
            ]
        )
    """

    references: list[Reference]
```

### edit_hyperparameters.py - Hyperparameter Update Request

```python
"""
Pydantic model for validating hyperparameter edit requests.
"""

from typing import Any
from pydantic import BaseModel, field_validator


class EditHyperparametersRequest(BaseModel):
    """
    Request model for updating session hyperparameters.

    Validates hyperparameter ranges:
    - temperature: 0-2
    - top_p: 0-1
    - max_tokens: positive integer

    Attributes:
        hyperparameters: Dictionary of hyperparameter values

    Examples:
        # Valid request
        request = EditHyperparametersRequest(
            hyperparameters={
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 4096,
            }
        )

        # Invalid request (temperature out of range)
        request = EditHyperparametersRequest(
            hyperparameters={"temperature": 3.0}  # Raises ValueError
        )
    """

    hyperparameters: dict[str, Any]

    @field_validator("hyperparameters")
    @classmethod
    def validate_hyperparameters(cls, v: dict[str, Any]) -> dict[str, Any]:
        """
        Validate hyperparameter values.

        Args:
            v: Hyperparameters dictionary

        Returns:
            Validated dictionary

        Raises:
            ValueError: If any parameter is out of valid range
        """
        # Validate temperature (0-2)
        temp = v.get("temperature")
        if temp is not None and not (0 <= temp <= 2):
            raise ValueError(
                f"Temperature must be between 0 and 2, got {temp}"
            )

        # Validate top_p (0-1)
        top_p = v.get("top_p")
        if top_p is not None and not (0 <= top_p <= 1):
            raise ValueError(
                f"Top_p must be between 0 and 1, got {top_p}"
            )

        # Validate max_tokens (positive)
        max_tokens = v.get("max_tokens")
        if max_tokens is not None and max_tokens <= 0:
            raise ValueError(
                f"Max_tokens must be positive, got {max_tokens}"
            )

        return v
```

### send_instruction.py - Instruction Request

```python
"""
Pydantic model for validating instruction requests.
"""

from pydantic import BaseModel, field_validator


class SendInstructionRequest(BaseModel):
    """
    Request model for sending instruction to existing session.

    Simple model that validates instruction is not empty.

    Attributes:
        instruction: Instruction text to execute

    Examples:
        request = SendInstructionRequest(
            instruction="Update the API endpoint"
        )
    """

    instruction: str

    @field_validator("instruction")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        """
        Validate instruction is not empty.

        Args:
            v: Instruction text

        Returns:
            Validated instruction

        Raises:
            ValueError: If instruction is empty
        """
        if not v or not v.strip():
            raise ValueError("Instruction must not be empty.")
        return v
```

## Validation Patterns

### Pattern 1: Non-Empty String

```python
@field_validator("field_name")
@classmethod
def check_not_empty(cls, v: str) -> str:
    if not v or not v.strip():
        raise ValueError("field_name must not be empty")
    return v
```

### Pattern 2: Range Validation

```python
@field_validator("temperature")
@classmethod
def validate_temperature(cls, v: float) -> float:
    if not (0 <= v <= 2):
        raise ValueError(f"temperature must be in range [0, 2], got {v}")
    return v
```

### Pattern 3: File Existence

```python
@field_validator("file_path")
@classmethod
def validate_file_exists(cls, v: str) -> str:
    if v and not os.path.isfile(v):
        raise ValueError(f"File not found: '{v}'")
    return v
```

### Pattern 4: List Validation

```python
@field_validator("items")
@classmethod
def validate_items(cls, v: list[str]) -> list[str]:
    if not v:
        raise ValueError("items must not be empty")

    for item in v:
        if not item.strip():
            raise ValueError("items must not contain empty strings")

    return v
```

## Testing

### Unit Testing Request Models

```python
# tests/web/requests/test_start_session.py
import pytest
from pipe.web.requests.sessions.start_session import StartSessionRequest
from pydantic import ValidationError


def test_start_session_request_valid():
    request = StartSessionRequest(
        purpose="Test purpose",
        background="Test background",
        instruction="Test instruction",
    )

    assert request.purpose == "Test purpose"
    assert request.background == "Test background"
    assert request.instruction == "Test instruction"
    assert request.multi_step_reasoning_enabled is False


def test_start_session_request_empty_purpose():
    with pytest.raises(ValidationError) as exc_info:
        StartSessionRequest(
            purpose="",  # Empty
            background="Test background",
            instruction="Test instruction",
        )

    assert "purpose must not be empty" in str(exc_info.value)


def test_start_session_request_with_options():
    request = StartSessionRequest(
        purpose="Test",
        background="Background",
        instruction="Do something",
        multi_step_reasoning_enabled=True,
        hyperparameters={"temperature": 0.7},
    )

    assert request.multi_step_reasoning_enabled is True
    assert request.hyperparameters["temperature"] == 0.7


def test_hyperparameters_request_invalid_temperature():
    with pytest.raises(ValidationError) as exc_info:
        EditHyperparametersRequest(
            hyperparameters={"temperature": 3.0}  # Out of range
        )

    assert "Temperature must be between 0 and 2" in str(exc_info.value)
```

## Best Practices

### 1. Validate All Inputs

```python
# ✅ GOOD: Validate all fields
class CreateRequest(BaseModel):
    name: str
    age: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name required")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v < 0:
            raise ValueError("Age must be positive")
        return v

# ❌ BAD: No validation
class CreateRequest(BaseModel):
    name: str
    age: int
    # No validators - relies on action to validate
```

### 2. Clear Error Messages

```python
# ✅ GOOD: Specific error message
@field_validator("temperature")
@classmethod
def validate(cls, v):
    if not (0 <= v <= 2):
        raise ValueError(f"temperature must be in range [0, 2], got {v}")
    return v

# ❌ BAD: Vague error message
@field_validator("temperature")
@classmethod
def validate(cls, v):
    if not (0 <= v <= 2):
        raise ValueError("Invalid value")  # Not helpful
    return v
```

### 3. Use External Validators for Complex Rules

```python
# ✅ GOOD: Reusable validator function
from pipe.web.validators.rules.file_exists import validate_list_of_files_exist

@field_validator("files")
@classmethod
def validate_files(cls, v: list[str]):
    validate_list_of_files_exist(v)  # Reusable
    return v

# ❌ BAD: Duplicate validation logic
@field_validator("files")
@classmethod
def validate_files(cls, v: list[str]):
    # Duplicating file validation logic
    for file in v:
        if not os.path.exists(file):
            raise ValueError(f"File not found: {file}")
    return v
```

### 4. Document Field Requirements

```python
# ✅ GOOD: Well-documented
class CreateRequest(BaseModel):
    """
    Request for creating resource.

    Attributes:
        name: Resource name (required, non-empty)
        description: Resource description (optional)
        tags: List of tags (optional, validated)
    """
    name: str
    description: str | None = None
    tags: list[str] | None = None

# ❌ BAD: No documentation
class CreateRequest(BaseModel):
    name: str
    description: str | None = None
    tags: list[str] | None = None
```

## Summary

Request models are **input validators**:

- ✅ Pydantic BaseModel subclasses
- ✅ Field validators for custom rules
- ✅ Clear error messages
- ✅ Type coercion and validation
- ✅ Self-documenting API
- ❌ No business logic
- ❌ No side effects
- ❌ No service calls

Validate early, validate thoroughly, fail fast with clear messages.
