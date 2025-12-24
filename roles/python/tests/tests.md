# Python Testing Strategy - src/pipe/core Layered Approach

## Purpose
This document defines a comprehensive testing strategy for each layer under `src/pipe/core`, outlining role definitions, factories, and available tools for automated test generation.

## Principles

### Layer Structure and Testing Philosophy

In Python, the idea that "mocking all dependencies allows ignoring layer structure" is **incorrect**. Since the purpose and strategy of testing differ for each layer, tests must be designed with an understanding of each layer's responsibilities.

**Important**: The Repository layer is responsible for verifying "whether actual file operations work correctly," so it should basically be tested using real file I/O with `tmp_path`, etc. Mocking `open()` or `json.dump()` would prevent detection of actual bugs such as path generation errors or directory creation failures.

```
Models (Data Structures)
  ↓
Domains (Business Logic)
  ↓
Collections (Collection Operations)
  ↓
Repositories (Persistence Layer) ← Test with real file I/O
  ↓
Services (Use Cases/Orchestration)
  ↓
Tools (External Tool Integration)
```

---

## Test Factory Design

### Factory Pattern

Factories are provided to eliminate duplication in test data generation and improve maintainability.

```python
# tests/factories/models/__init__.py
"""Test data factories for unit tests."""

from .session_factory import SessionFactory
from .turn_factory import TurnFactory
from .settings_factory import SettingsFactory

__all__ = [
    "SessionFactory",
    "TurnFactory",
    "SettingsFactory",
]
```

```python
# tests/factories/models/session_factory.py
"""Factory for creating Session test fixtures."""

from typing import Optional
from pipe.core.models.session import Session
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.collections.turns import TurnCollection


class SessionFactory:
    """Factory class for creating Session objects in tests."""

    @staticmethod
    def create(
        session_id: str = "test-session-123",
        created_at: str = "2025-01-01T00:00:00+09:00",
        purpose: Optional[str] = "Test session purpose",
        background: Optional[str] = "Test background",
        roles: Optional[list[str]] = None,
        multi_step_reasoning_enabled: bool = False,
        **kwargs
    ) -> Session:
        """Create a Session object with default test values.

        Args:
            session_id: Session ID (default: "test-session-123")
            created_at: Creation timestamp (default: "2025-01-01T00:00:00+09:00")
            purpose: Session purpose
            background: Session background
            roles: List of roles
            multi_step_reasoning_enabled: Enable multi-step reasoning
            **kwargs: Additional fields to override

        Returns:
            Session object
        """
        return Session(
            session_id=session_id,
            created_at=created_at,
            purpose=purpose,
            background=background,
            roles=roles or [],
            multi_step_reasoning_enabled=multi_step_reasoning_enabled,
            **kwargs
        )

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[Session]:
        """Create multiple Session objects.

        Args:
            count: Number of sessions to create
            **kwargs: Arguments passed to create()

        Returns:
            List of Session objects
        """
        return [
            SessionFactory.create(
                session_id=f"test-session-{i}",
                **kwargs
            )
            for i in range(count)
        ]

    @staticmethod
    def create_with_turns(turn_count: int = 3, **kwargs) -> Session:
        """Create a Session with predefined turns.

        Args:
            turn_count: Number of turns to create
            **kwargs: Arguments passed to create()

        Returns:
            Session object with turns
        """
        from .turn_factory import TurnFactory

        turns = TurnFactory.create_batch(turn_count)
        return SessionFactory.create(turns=TurnCollection(turns), **kwargs)


# tests/factories/models/turn_factory.py
"""Factory for creating Turn test fixtures."""

from pipe.core.models.turn import (
    UserTaskTurn,
    ModelResponseTurn,
    FunctionCallingTurn,
)


class TurnFactory:
    """Factory class for creating Turn objects in tests."""

    @staticmethod
    def create_user_task(
        instruction: str = "Test instruction",
        timestamp: str = "2025-01-01T00:00:00+09:00",
        **kwargs
    ) -> UserTaskTurn:
        """Create a UserTaskTurn object."""
        return UserTaskTurn(
            type="user_task",
            instruction=instruction,
            timestamp=timestamp,
            **kwargs
        )

    @staticmethod
    def create_model_response(
        content: str = "Test response",
        timestamp: str = "2025-01-01T00:01:00+09:00",
        **kwargs
    ) -> ModelResponseTurn:
        """Create a ModelResponseTurn object."""
        return ModelResponseTurn(
            type="model_response",
            content=content,
            timestamp=timestamp,
            **kwargs
        )

    @staticmethod
    def create_batch(count: int, alternate: bool = True) -> list:
        """Create multiple Turn objects.

        Args:
            count: Number of turns to create
            alternate: If True, alternate between user_task and model_response

        Returns:
            List of Turn objects
        """
        turns = []
        for i in range(count):
            if alternate and i % 2 == 0:
                turns.append(TurnFactory.create_user_task(instruction=f"Instruction {i}"))
            else:
                turns.append(TurnFactory.create_model_response(content=f"Response {i}"))
        return turns


# tests/factories/models/settings_factory.py
"""Factory for creating Settings test fixtures."""

from unittest.mock import Mock
from pipe.core.models.settings import Settings


class SettingsFactory:
    """Factory class for creating Settings objects in tests."""

    @staticmethod
    def create_mock(
        timezone: str = "Asia/Tokyo",
        sessions_path: str = ".sessions",
        reference_ttl: int = 3,
        **kwargs
    ) -> Mock:
        """Create a mock Settings object for testing.

        Args:
            timezone: Timezone string
            sessions_path: Path to sessions directory
            reference_ttl: Reference time-to-live
            **kwargs: Additional attributes

        Returns:
            Mock Settings object
        """
        settings = Mock(spec=Settings)
        settings.timezone = timezone
        settings.sessions_path = sessions_path
        settings.reference_ttl = reference_ttl

        for key, value in kwargs.items():
            setattr(settings, key, value)

        return settings
```

### Usage Example

```python
# tests/unit/core/services/test_session_service.py
from tests.factories.models import SessionFactory, SettingsFactory


def test_example_with_factories():
    """Example test using factories."""
    # Concisely generate test data
    session = SessionFactory.create(purpose="Custom purpose")
    sessions = SessionFactory.create_batch(5)
    settings = SettingsFactory.create_mock(timezone="UTC")

    # Test logic
    assert session.purpose == "Custom purpose"
    assert len(sessions) == 5
```

---

## pytest Configuration and Best Practices

### Running pytest

**CRITICAL**: This project uses **Poetry** for dependency management. Always run pytest through Poetry:

```bash
# ✅ CORRECT - Run pytest through Poetry
poetry run pytest

# ✅ CORRECT - Run specific test file
poetry run pytest tests/unit/core/models/test_session.py

# ✅ CORRECT - Run with coverage
poetry run pytest --cov=src/pipe/core

# ❌ WRONG - Do NOT run pytest directly
pytest  # This may use wrong Python environment or missing dependencies
```

### Using MCP Tools for Test Development

For larger or complex test suites, leverage MCP (Model Context Protocol) tools to improve efficiency:

- **`py_test_strategist`**: Analyze production code and generate comprehensive test strategies
  - Use when: Planning tests for complex modules or entire layers
  - Example: Generating test plan for a new Service class

- **`py_dependency_tree`**: Visualize module dependencies and identify test requirements
  - Use when: Understanding what needs to be mocked or which modules to test first
  - Example: Mapping dependencies before writing Repository tests

- **`py_auto_format_code`**: Automatically format test code to project standards
  - Use when: Generated test code needs formatting cleanup
  - Example: After generating multiple test files

**Guideline**: Use these tools proactively for non-trivial test generation tasks. For small, straightforward tests (single function, simple model), manual generation is sufficient.

### pytest.ini Settings

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --strict-markers
    --cov=src/pipe/core
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=90
markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (may use real files/databases)
    slow: Slow tests (skipped by default)
    security: Security-related tests (command injection, etc.)
```

**Coverage Goals**:
- **Core Layer (models, domains, repositories, services)**: 95% or higher
- **Tools Layer**: 80% or higher (due to many external dependencies)
- **Overall**: 90% or higher (enforced by `--cov-fail-under=90`)

### Shared Fixtures

```python
# tests/conftest.py
"""Shared pytest fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_project_root():
    """Create a temporary project root directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_sessions_dir(temp_project_root):
    """Create a temporary sessions directory."""
    sessions_dir = Path(temp_project_root) / ".sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return str(sessions_dir)
```

---

## Available Tools and Libraries

### Test Framework
- **pytest**: Main test framework
- **pytest-cov**: Coverage measurement
- **pytest-mock**: Mocking extension (optional)

### Mock Libraries
- **unittest.mock**: Standard library
  - `Mock`, `MagicMock`: Basic mocks
  - `patch`: Function/Class mocking
  - `patch.object`: Object method mocking

### Assertion Helpers
- **pytest assertions**: Detailed error messages
- **pytest.raises**: Exception testing
- **pytest.warns**: Warning testing

### Test Data Generation
- **tests/factories**: Custom factories (defined in this document)
- **Faker** (optional): Random data generation
- **factory_boy** (optional): Advanced factory patterns

---

## Test Generation Quality Standards

When generating tests, the following quality standards must be strictly followed to ensure test code quality and maintainability.

### Required Elements

1. **Docstrings**: Every test class and test method must have clear docstrings describing their purpose
   ```python
   class TestSessionModel:
       """Session model validation and serialization tests."""

       def test_valid_session_creation(self):
           """Test creating a valid session with all required fields."""
   ```

2. **Fixtures**: Extract common setup logic into pytest fixtures. Service layer fixtures MUST create new instances for each test to prevent state leakage
   ```python
   @pytest.fixture
   def service(mock_repository, mock_settings):
       """Create a SessionService instance.

       IMPORTANT: Creates new instance per test to prevent state leakage
       (current_session, etc.)
       """
       return SessionService(repository=mock_repository, settings=mock_settings)
   ```

3. **Clear Assertions**: Use specific and meaningful assertions with descriptive failure messages
   ```python
   # Good
   assert session.session_id == "test-123"
   assert len(sessions) == 5

   # Bad
   assert session  # Unclear what is being tested
   assert result   # Too vague
   ```

4. **Edge Case Coverage**: Test both normal cases and edge cases (empty collections, boundary values, null values, etc.)
   ```python
   def test_empty_collection(self):
       """Test behavior with empty collection."""

   def test_index_out_of_range(self):
       """Test that out-of-range index raises IndexError."""
   ```

5. **Factory Usage**: Always use `tests/factories` for test data generation instead of creating models inline
   ```python
   # Good
   session = SessionFactory.create(purpose="Custom purpose")

   # Bad
   session = Session(
       session_id="test-123",
       created_at="2025-01-01T00:00:00+09:00",
       purpose="Custom purpose",
       # ... many fields
   )
   ```

6. **Immutability Verification**: For Domain layer functions, verify that original data is not modified
   ```python
   def test_domain_function_does_not_mutate_original(self):
       """Test that domain function preserves immutability."""
       original_copy = original.model_copy(deep=True)
       result = domain_function(original)
       assert original == original_copy  # Original unchanged
   ```

7. **Security Testing**: For Tools layer, include tests for command injection, path traversal, and other security vulnerabilities
   ```python
   @pytest.mark.security
   def test_command_injection_prevention(self):
       """Test that command injection attempts are blocked."""
       dangerous_commands = ["echo hello; rm -rf /", "cat /etc/passwd"]
       for cmd in dangerous_commands:
           with pytest.raises((ValueError, SecurityError)):
               run_shell_command(command=cmd)
   ```

### Prohibited Items

- ❌ **No real file I/O** (except Repository layer which uses `tmp_path`)
- ❌ **No actual external API requests** (use mocks or fixtures)
- ❌ **No hardcoded paths** (use `tmp_path`, `tempfile`, or fixtures)
- ❌ **No test dependencies** (each test must run independently)
- ❌ **No unclear assertions** (avoid `assert result` without context)
- ❌ **No state leakage** between tests (use fixtures with proper scope)
- ❌ **No unnecessary mocks** for pure functions (Models/Domains/Collections)

### Mandatory Requirements

#### Pydantic V2 Compatibility

**ALL code must be compatible with Pydantic V2.** Use the following patterns:

```python
# Serialization (Pydantic V2)
session.model_dump(by_alias=True)     # Returns dict with camelCase (aliases)
session.model_dump_json(by_alias=True) # Returns JSON string with camelCase

# NOTE: model_dump(mode="json") does NOT use aliases - it only affects value serialization
# To get camelCase field names, you MUST use by_alias=True

# Deserialization (Pydantic V2)
Session.model_validate(data)         # Create from dict
Session.model_validate_json(json_str) # Create from JSON string

# Copying (Pydantic V2)
session.model_copy(deep=True)        # Deep copy

# PROHIBITED (Pydantic V1 - DO NOT USE)
session.dict()                        # ❌ Deprecated
Session.parse_obj(data)               # ❌ Deprecated
session.copy(deep=True)               # ❌ Deprecated
```

#### Report Production Code Changes

**CRITICAL**: If test generation requires changes to production code (non-test files), you **MUST** report this explicitly before making any changes.

... (same as before) ...

**Do NOT make production code changes without explicit user approval.**

#### Static Analysis and Linting (Mandatory)

**CRITICAL**: After any code modification, you **MUST** run `py_checker` to ensure there are no linting (Ruff) or type (MyPy) errors across the project. A 100% pass rate is required for all new or modified files.

---

## Summary

- **Layer structure is important**: Even when using mocks, a testing strategy tailored to each layer's responsibilities is necessary.
- **Factories are effective**: Eliminate duplication in test data generation and improve maintainability.
- **Mock usage**:
  - Models/Domains/Collections → No mocks needed (Pure logic/Data structures)
  - Repositories → Basically real file I/O (verify with tmp_path), mock only abnormal cases
  - Services → Mock Repository layer (focus on use case logic)
  - Tools → Mock all external dependencies (subprocess, API calls, etc.)
- **Quality standards**: Follow required elements, avoid prohibited items, ensure Pydantic V2 compatibility, and always report production code changes

---

