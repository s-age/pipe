# Validators Layer

## Purpose

Validators provide **reusable validation functions** for custom business rules that are used across multiple request models. They centralize common validation logic.

**Note**: With the new BaseRequest pattern, many validations can be done directly in request models using `@field_validator`. Use this layer only for truly reusable validation logic shared across multiple requests.

## Responsibilities

1. **Reusable Validation** - Functions used by multiple request models
2. **Custom Rules** - Business-specific validation logic
3. **Clear Errors** - Raise ValueError with descriptive messages
4. **Pure Functions** - No side effects, only validation
5. **Independent** - No dependencies on request models

## When to Use

**Use validators when:**

- ✅ Same validation logic is needed in multiple request models
- ✅ Complex validation that would clutter request models
- ✅ External resource validation (files, databases, etc.)

**Don't use validators when:**

- ❌ Validation is specific to one request model (use `@field_validator`)
- ❌ Simple type/format checks (Pydantic handles these)
- ❌ Business logic (belongs in services)

## Characteristics

- ✅ Pure validation functions
- ✅ Raise ValueError on failure
- ✅ Clear error messages
- ✅ Reusable across request models
- ✅ No side effects
- ❌ **NO business logic** - only validation
- ❌ **NO state** - pure functions
- ❌ **NO service calls** - no external dependencies

## File Structure

```
validators/
├── __init__.py
└── rules/
    ├── __init__.py
    └── file_exists.py    # File existence validation
```

## Dependencies

**Allowed:**

- ✅ Standard library (os, re, etc.)
- ✅ No dependencies is best

**Forbidden:**

- ❌ Core Services (no business logic calls)
- ❌ Core Repositories (no data access)
- ❌ Request Models (validators are independent)
- ❌ Actions (no action calls)

## Template

```python
"""
Validation rules for [domain].

Provides reusable validation functions that can be used
in multiple request models.
"""


def validate_something(value: str) -> None:
    """
    Validates that something meets requirements.

    This is a pure validation function with no side effects.
    It raises ValueError if validation fails.

    Args:
        value: Value to validate

    Raises:
        ValueError: If validation fails with descriptive message

    Examples:
        # Valid - no error
        validate_something("valid_value")

        # Invalid - raises ValueError
        validate_something("invalid")  # ValueError: ...
    """
    if not is_valid(value):
        raise ValueError(f"Invalid value: '{value}'")


def validate_list_of_something(values: list[str]) -> None:
    """
    Validates a list of values.

    Args:
        values: List of values to validate

    Raises:
        ValueError: If any value is invalid

    Examples:
        validate_list_of_something(["a", "b", "c"])
    """
    if not values:
        return  # Empty list is valid

    for value in values:
        validate_something(value)
```

## Real Example

### file_exists.py - File Existence Validation

```python
"""
Validation rules for file existence.

Provides reusable functions to validate that files exist
before they're used in the application.
"""

import os
import re


def validate_file_exists(path: str) -> None:
    """
    Validates that a file exists at the given path.

    This is a fundamental validation used throughout the
    web layer to ensure file paths are valid before passing
    them to core services.

    The path is cleaned (stripped of quotes and whitespace)
    before validation.

    Args:
        path: File path to validate

    Raises:
        ValueError: If file doesn't exist

    Examples:
        # Valid file
        validate_file_exists("src/main.py")

        # Invalid file
        validate_file_exists("nonexistent.py")  # ValueError

        # Handles quoted paths
        validate_file_exists("'src/main.py'")  # Strips quotes
    """
    clean_path = path.strip().strip("'\"")

    if not os.path.exists(clean_path):
        raise ValueError(f"File not found: '{clean_path}'")


def validate_comma_separated_files(paths: str) -> None:
    """
    Validates a comma-separated string of file paths.

    This is useful for CLI-style inputs where multiple
    files are specified as "file1.py,file2.py,file3.py".

    Args:
        paths: Comma-separated file paths

    Raises:
        ValueError: If any file doesn't exist

    Examples:
        # Valid
        validate_comma_separated_files("src/a.py,src/b.py")

        # Invalid
        validate_comma_separated_files("a.py,nonexistent.py")  # ValueError

        # Empty string is valid
        validate_comma_separated_files("")
    """
    if not paths:
        return  # Empty string is valid

    for path in paths.split(","):
        if path.strip():
            validate_file_exists(path.strip())


def validate_space_separated_files(paths: str) -> None:
    """
    Validates a space-separated string of file paths.

    Respects quoted paths (e.g., "file with spaces.py").
    Useful for CLI-style inputs where files might contain spaces.

    Args:
        paths: Space-separated file paths (respects quotes)

    Raises:
        ValueError: If any file doesn't exist

    Examples:
        # Valid
        validate_space_separated_files('src/a.py src/b.py')

        # With quoted paths
        validate_space_separated_files('"file with spaces.py" other.py')

        # Invalid
        validate_space_separated_files('a.py nonexistent.py')  # ValueError
    """
    if not paths:
        return

    # Split by space, respecting quoted paths
    # Regex: split on spaces not inside quotes
    pattern = r'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)'
    reference_files = re.split(pattern, paths.strip())

    for path in reference_files:
        if path.strip():
            validate_file_exists(path)


def validate_list_of_files_exist(paths: list[str]) -> None:
    """
    Validates that all files in a list of paths exist.

    This is the most common validation function, used by
    request models that accept lists of file paths.

    Args:
        paths: List of file paths to validate

    Raises:
        ValueError: If any file doesn't exist

    Examples:
        # Valid
        validate_list_of_files_exist([
            "src/main.py",
            "src/utils.py",
        ])

        # Invalid
        validate_list_of_files_exist([
            "src/main.py",
            "nonexistent.py",  # ValueError
        ])

        # Empty list is valid
        validate_list_of_files_exist([])

        # None is valid
        validate_list_of_files_exist(None)
    """
    if not paths:
        return  # Empty or None is valid

    for path in paths:
        if path.strip():
            validate_file_exists(path.strip())
```

## Validation Patterns

### Pattern 1: Simple Validation

```python
def validate_not_empty(value: str) -> None:
    """Validate string is not empty."""
    if not value or not value.strip():
        raise ValueError("Value must not be empty")
```

### Pattern 2: Range Validation

```python
def validate_in_range(value: float, min_val: float, max_val: float) -> None:
    """Validate value is in range."""
    if not (min_val <= value <= max_val):
        raise ValueError(
            f"Value must be in range [{min_val}, {max_val}], got {value}"
        )
```

### Pattern 3: Format Validation

```python
import re

def validate_email_format(email: str) -> None:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        raise ValueError(f"Invalid email format: '{email}'")
```

### Pattern 4: List Validation

```python
def validate_unique_items(items: list[str]) -> None:
    """Validate list has no duplicates."""
    seen = set()

    for item in items:
        if item in seen:
            raise ValueError(f"Duplicate item: '{item}'")
        seen.add(item)
```

## Usage in Request Models

### Example 1: File Validation

```python
# In request model
from pipe.web.validators.rules.file_exists import validate_list_of_files_exist
from pydantic import BaseModel, field_validator


class StartSessionRequest(BaseModel):
    roles: list[str] | None = None

    @field_validator("roles")
    @classmethod
    def validate_roles_exist(cls, v: list[str]) -> list[str]:
        # Use reusable validator
        validate_list_of_files_exist(v)
        return v
```

### Example 2: Custom Validation

```python
# In validators/rules/format.py
def validate_session_id_format(session_id: str) -> None:
    """Validate session ID format."""
    if not re.match(r'^[a-z0-9-]+$', session_id):
        raise ValueError(
            f"Invalid session ID format: '{session_id}'. "
            "Must contain only lowercase letters, numbers, and hyphens."
        )


# In request model
from pipe.web.validators.rules.format import validate_session_id_format

class GetSessionRequest(BaseModel):
    session_id: str

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        validate_session_id_format(v)
        return v
```

## Testing

### Unit Testing Validators

```python
# tests/web/validators/test_file_exists.py
import os
import tempfile
import pytest
from pipe.web.validators.rules.file_exists import (
    validate_file_exists,
    validate_list_of_files_exist,
    validate_comma_separated_files,
)


def test_validate_file_exists_success():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name

    try:
        # Should not raise
        validate_file_exists(temp_path)
    finally:
        os.remove(temp_path)


def test_validate_file_exists_not_found():
    with pytest.raises(ValueError) as exc_info:
        validate_file_exists("nonexistent_file.txt")

    assert "File not found" in str(exc_info.value)
    assert "nonexistent_file.txt" in str(exc_info.value)


def test_validate_file_exists_strips_quotes():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name

    try:
        # Should strip quotes and validate
        validate_file_exists(f"'{temp_path}'")
        validate_file_exists(f'"{temp_path}"')
    finally:
        os.remove(temp_path)


def test_validate_list_of_files_exist_success():
    with tempfile.NamedTemporaryFile(delete=False) as f1, \
         tempfile.NamedTemporaryFile(delete=False) as f2:
        paths = [f1.name, f2.name]

    try:
        # Should not raise
        validate_list_of_files_exist(paths)
    finally:
        os.remove(f1.name)
        os.remove(f2.name)


def test_validate_list_of_files_exist_one_missing():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name

    try:
        paths = [temp_path, "nonexistent.txt"]

        with pytest.raises(ValueError) as exc_info:
            validate_list_of_files_exist(paths)

        assert "File not found" in str(exc_info.value)
        assert "nonexistent.txt" in str(exc_info.value)
    finally:
        os.remove(temp_path)


def test_validate_list_of_files_exist_empty_list():
    # Empty list should be valid
    validate_list_of_files_exist([])
    validate_list_of_files_exist(None)


def test_validate_comma_separated_files():
    with tempfile.NamedTemporaryFile(delete=False) as f1, \
         tempfile.NamedTemporaryFile(delete=False) as f2:
        paths_str = f"{f1.name},{f2.name}"

    try:
        # Should not raise
        validate_comma_separated_files(paths_str)
    finally:
        os.remove(f1.name)
        os.remove(f2.name)


def test_validate_comma_separated_files_empty():
    # Empty string should be valid
    validate_comma_separated_files("")
    validate_comma_separated_files(None)
```

## Best Practices

### 1. Keep Validators Pure

```python
# ✅ GOOD: Pure function
def validate_file_exists(path: str) -> None:
    if not os.path.exists(path):
        raise ValueError(f"File not found: '{path}'")

# ❌ BAD: Side effects
def validate_file_exists(path: str) -> None:
    if not os.path.exists(path):
        logging.error(f"File not found: {path}")  # Side effect
        raise ValueError(f"File not found: '{path}'")
```

### 2. Clear Error Messages

```python
# ✅ GOOD: Specific error message
def validate_range(value: float) -> None:
    if not (0 <= value <= 1):
        raise ValueError(f"Value must be in range [0, 1], got {value}")

# ❌ BAD: Vague error message
def validate_range(value: float) -> None:
    if not (0 <= value <= 1):
        raise ValueError("Invalid value")  # Not helpful
```

### 3. Handle Edge Cases

```python
# ✅ GOOD: Handle None and empty
def validate_list(items: list[str] | None) -> None:
    if not items:
        return  # None or empty is valid

    for item in items:
        if item.strip():
            validate_item(item)

# ❌ BAD: Doesn't handle None
def validate_list(items: list[str]) -> None:
    for item in items:  # Crashes if items is None
        validate_item(item)
```

### 4. Make Validators Reusable

```python
# ✅ GOOD: Generic, reusable
def validate_file_exists(path: str) -> None:
    """Can be used anywhere."""
    if not os.path.exists(path):
        raise ValueError(f"File not found: '{path}'")

# ❌ BAD: Too specific
def validate_role_file_exists(path: str) -> None:
    """Only for roles - not reusable."""
    if not os.path.exists(path):
        raise ValueError(f"Role file not found: '{path}'")
```

### 5. Separate Concerns

```python
# ✅ GOOD: Validation only
def validate_email(email: str) -> None:
    if not is_valid_email_format(email):
        raise ValueError(f"Invalid email: '{email}'")

# ❌ BAD: Validation + transformation
def validate_email(email: str) -> str:
    # Validators shouldn't transform
    return email.lower().strip()
```

## Summary

Validators are **pure validation functions**:

- ✅ Reusable across request models
- ✅ Pure functions (no side effects)
- ✅ Raise ValueError on failure
- ✅ Clear, descriptive error messages
- ✅ Independent of request models
- ❌ No business logic
- ❌ No state
- ❌ No service calls
- ❌ No side effects

Keep validators simple, pure, and reusable.
