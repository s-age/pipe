"""Unit tests for the Session model."""

import json

import pytest
from pipe.core.models.session import Session
from pipe.core.models.todo import TodoItem
from pydantic import ValidationError

from tests.factories.models import SessionFactory


class TestSessionModel:
    """Session model validation and serialization tests."""

    def test_valid_session_creation(self):
        """Test creating a valid session with all required fields."""
        session = SessionFactory.create(
            session_id="test-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Test session",
            background="Test background",
        )
        assert session.session_id == "test-123"
        assert session.multi_step_reasoning_enabled is False  # default
        assert session.token_count == 0  # default
        assert isinstance(session.roles, list)
        assert session.purpose == "Test session"

    def test_session_validation_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Session(created_at="2025-01-01T00:00:00+09:00")
        assert "sessionId" in str(exc_info.value)

    def test_session_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        session = SessionFactory.create(
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
        # Use model_validate to trigger the validator
        data = {
            "session_id": "test-123",
            "created_at": "2025-01-01T00:00:00+09:00",
            "multi_step_reasoning_enabled": None,
        }
        session = Session.model_validate(data)
        assert session.multi_step_reasoning_enabled is False

    def test_session_todos_preprocessing_strings(self):
        """Test that string todos are converted to TodoItem objects."""
        data = {
            "session_id": "test-123",
            "created_at": "2025-01-01T00:00:00+09:00",
            "todos": ["Task 1", "Task 2"],
        }
        session = Session.model_validate(data)
        assert len(session.todos) == 2
        assert all(isinstance(t, TodoItem) for t in session.todos)
        assert session.todos[0].title == "Task 1"
        assert session.todos[1].title == "Task 2"

    def test_session_todos_preprocessing_dicts(self):
        """Test that dict todos are converted to TodoItem objects."""
        data = {
            "session_id": "test-123",
            "created_at": "2025-01-01T00:00:00+09:00",
            "todos": [{"title": "Task 1", "checked": True}, {"title": "Task 2"}],
        }
        session = Session.model_validate(data)
        assert len(session.todos) == 2
        assert session.todos[0].title == "Task 1"
        assert session.todos[0].checked is True
        assert session.todos[1].title == "Task 2"
        assert session.todos[1].checked is False

    def test_session_model_dump_json_string(self):
        """Test serialization with model_dump_json() returns a JSON string."""
        session = SessionFactory.create(
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
        original = SessionFactory.create(
            session_id="roundtrip-123",
            created_at="2025-01-01T00:00:00+09:00",
            purpose="Test purpose",
            background="Test background",
            roles=["Developer", "Tester"],
            multi_step_reasoning_enabled=True,
            todos=["Task 1"],
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
        assert (
            restored.multi_step_reasoning_enabled
            == original.multi_step_reasoning_enabled
        )
        assert len(restored.todos) == 1
        assert restored.todos[0].title == "Task 1"

    def test_session_with_turns_serialization(self):
        """Test that sessions with turns can be serialized/deserialized."""
        session = SessionFactory.create_with_turns(turn_count=2)

        # Serialize
        json_str = session.model_dump_json(by_alias=True)
        data = json.loads(json_str)

        # Verify turns are in the JSON
        assert "turns" in data
        assert len(data["turns"]) == 2

        # Deserialize
        restored = Session.model_validate(data)
        assert len(restored.turns) == 2
        assert restored.turns[0].type == "user_task"
        assert restored.turns[1].type == "model_response"
