# Models Layer Testing Strategy

**Layer:** `src/pipe/core/models/`

## Responsibilities
- Data structure definitions using Pydantic models
- Validation rule definitions
- Serialization/Deserialization

## Testing Strategy
- **No Mocks Needed**: Testing pure data structures
- **Focus**: Validation, default values, type conversion, alias handling

## Test Patterns

```python
# tests/unit/core/models/test_session.py
import pytest
from pipe.core.models.session import Session, SessionInputData
from pipe.core.models.hyperparameters import Hyperparameters
from pydantic import ValidationError


class TestSessionModel:
    """Session model validation and serialization tests."""

    def test_valid_session_creation(self):
        """Test creating a valid session with all required fields."""
        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Test session",
            background="Test background",
        )
        assert session.session_id == "test-123"
        assert session.multi_step_reasoning_enabled is False  # default
        assert session.token_count == 0  # default

    def test_session_validation_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Session(created_at="2025-01-01T00:00:00+09:00")
        assert "session_id" in str(exc_info.value)

    def test_session_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
        )
        # Use by_alias=True to get camelCase field names
        dumped = session.model_dump(by_alias=True)
        assert dumped["sessionId"] == "test-123"  # camelCase conversion
        assert "createdAt" in dumped

        # Without by_alias=True, field names remain snake_case
        dumped_no_alias = session.model_dump()
        assert dumped_no_alias["session_id"] == "test-123"  # snake_case

    def test_session_preprocess_multi_step_reasoning_null(self):
        """Test that null multi_step_reasoning_enabled is converted to False."""
        data: SessionInputData = {
            "session_id": "test-123",
            "created_at": "2025-01-01T00:00:00+09:00",
            "multi_step_reasoning_enabled": None,
        }
        session = Session.model_validate(data)
        assert session.multi_step_reasoning_enabled is False

    def test_session_todos_preprocessing(self):
        """Test that string todos are converted to TodoItem objects."""
        data: SessionInputData = {
            "session_id": "test-123",
            "created_at": "2025-01-01T00:00:00+09:00",
            "todos": ["Task 1", "Task 2"],
        }
        session = Session.model_validate(data)
        assert len(session.todos) == 2
        assert session.todos[0].title == "Task 1"

    def test_session_model_dump_json_string(self):
        """Test serialization with model_dump_json() returns a JSON string."""
        import json

        session = Session(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Test purpose",
        )

        # model_dump_json() with by_alias=True to get camelCase
        json_str = session.model_dump_json(by_alias=True)

        # Verify it's a valid JSON string
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["sessionId"] == "test-123"  # camelCase field name
        assert parsed["purpose"] == "Test purpose"

    def test_session_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        import json

        original = Session(
            session_id="roundtrip-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Test purpose",
            background="Test background",
            roles=["Developer", "Tester"],
            multi_step_reasoning_enabled=True,
        )

        # Serialize to JSON string (by_alias=True for camelCase)
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back (populate_by_name=True allows both camelCase and snake_case)
        data = json.loads(json_str)
        restored = Session.model_validate(data)

        # Verify all fields are preserved
        assert restored.session_id == original.session_id
        assert restored.purpose == original.purpose
        assert restored.background == original.background
        assert restored.roles == original.roles
        assert restored.multi_step_reasoning_enabled == original.multi_step_reasoning_enabled
```

## Mandatory Test Items
- ✅ Validation of required fields
- ✅ Validation of default values
- ✅ Serialization with `model_dump(by_alias=True)` for camelCase output
- ✅ Deserialization with `model_validate()`
- ✅ Logic of custom validators (`@model_validator`)
- ✅ Alias conversion (camelCase ↔ snake_case)
- ✅ Roundtrip serialization (serialize → deserialize → verify)
