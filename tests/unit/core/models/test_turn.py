import pytest
from pipe.core.models.turn import (
    ModelResponseTurn,
    ModelResponseTurnUpdate,
    ToolResponseTurn,
    Turn,
    UserTaskTurn,
    UserTaskTurnUpdate,
)
from pydantic import TypeAdapter, ValidationError

from tests.helpers.turn_factory import TurnFactory


class TestTurnModels:
    """Tests for Turn models validation and serialization."""

    def test_user_task_turn_creation(self):
        """Test creating a valid UserTaskTurn."""
        turn = TurnFactory.create_user_task(
            instruction="Hello", timestamp="2025-01-01T00:00:00Z"
        )
        assert turn.type == "user_task"
        assert turn.instruction == "Hello"
        assert turn.timestamp == "2025-01-01T00:00:00Z"

    def test_model_response_turn_creation(self):
        """Test creating a valid ModelResponseTurn with optional fields."""
        turn = TurnFactory.create_model_response(
            content="Hi there",
            thought="Thinking...",
            raw_response="RAW",
            timestamp="2025-01-01T00:01:00Z",
        )
        assert turn.type == "model_response"
        assert turn.content == "Hi there"
        assert turn.thought == "Thinking..."
        assert turn.raw_response == "RAW"
        assert turn.timestamp == "2025-01-01T00:01:00Z"

    def test_function_calling_turn_creation(self):
        """Test creating a valid FunctionCallingTurn."""
        turn = TurnFactory.create_function_calling(
            response="call_1", raw_response="RAW_CALL", timestamp="2025-01-01T00:02:00Z"
        )
        assert turn.type == "function_calling"
        assert turn.response == "call_1"
        assert turn.raw_response == "RAW_CALL"

    def test_tool_response_turn_creation(self):
        """Test creating a valid ToolResponseTurn."""
        turn = TurnFactory.create_tool_response(
            name="get_weather",
            status="success",
            message="Sunny",
            timestamp="2025-01-01T00:03:00Z",
        )
        assert turn.type == "tool_response"
        assert turn.name == "get_weather"
        assert turn.response.status == "success"
        assert turn.response.message == "Sunny"

    def test_compressed_history_turn_creation(self):
        """Test creating a valid CompressedHistoryTurn."""
        turn = TurnFactory.create_compressed_history(
            content="Summary",
            original_turns_range=[1, 10],
            timestamp="2025-01-01T00:04:00Z",
        )
        assert turn.type == "compressed_history"
        assert turn.content == "Summary"
        assert turn.original_turns_range == [1, 10]

    def test_turn_union_validation(self):
        """Test that the Turn union correctly identifies turn types."""
        data = {
            "type": "user_task",
            "instruction": "Test",
            "timestamp": "2025-01-01T00:00:00Z",
        }
        turn = TypeAdapter(Turn).validate_python(data)
        assert isinstance(turn, UserTaskTurn)

        data = {
            "type": "model_response",
            "content": "Test",
            "timestamp": "2025-01-01T00:00:00Z",
        }
        turn = TypeAdapter(Turn).validate_python(data)
        assert isinstance(turn, ModelResponseTurn)

    def test_user_task_turn_update_validation(self):
        """Test UserTaskTurnUpdate validation and forbid extra fields."""
        # Valid partial update
        update = UserTaskTurnUpdate(instruction="New instruction")
        assert update.instruction == "New instruction"
        assert update.timestamp is None

        # Forbid extra fields
        with pytest.raises(ValidationError):
            UserTaskTurnUpdate(instruction="New", extra_field="not allowed")

    def test_model_response_turn_update_validation(self):
        """Test ModelResponseTurnUpdate validation and forbid extra fields."""
        update = ModelResponseTurnUpdate(content="New content", thought="New thought")
        assert update.content == "New content"
        assert update.thought == "New thought"

        with pytest.raises(ValidationError):
            ModelResponseTurnUpdate(content="New", extra_field="not allowed")

    def test_serialization_roundtrip_with_aliases(self):
        """Test serialization and deserialization preserve data and handle camelCase
        aliases.
        """
        original = TurnFactory.create_model_response(
            content="Response", raw_response="RAW", thought="Thought"
        )

        # Serialize to dict with aliases (camelCase)
        dumped = original.model_dump(by_alias=True)
        assert "rawResponse" in dumped
        assert dumped["rawResponse"] == "RAW"
        assert "thought" in dumped
        assert dumped["thought"] == "Thought"

        # Deserialize back
        restored = ModelResponseTurn.model_validate(dumped)
        assert restored.raw_response == "RAW"
        assert restored.thought == "Thought"
        assert restored.content == "Response"

    def test_tool_response_serialization_with_extra_fields(self):
        """Test that TurnResponse allows extra fields as configured."""
        data = {
            "type": "tool_response",
            "name": "test",
            "timestamp": "2025-01-01T00:00:00Z",
            "response": {
                "status": "success",
                "message": "done",
                "extra_info": "something extra",
            },
        }
        turn = ToolResponseTurn.model_validate(data)
        assert turn.response.status == "success"
        # Since extra="allow" is set in TurnResponse's model_config
        assert getattr(turn.response, "extra_info", None) == "something extra"

    def test_invalid_turn_type_raises_validation_error(self):
        """Test that an invalid turn type raises ValidationError."""
        with pytest.raises(ValidationError):
            TypeAdapter(Turn).validate_python(
                {"type": "invalid_type", "timestamp": "2025-01-01T00:00:00Z"}
            )
