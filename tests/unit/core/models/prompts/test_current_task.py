import json

import pytest
from pipe.core.models.prompts.current_task import PromptCurrentTask
from pipe.core.models.turn import TurnResponse
from pydantic import ValidationError


class TestPromptCurrentTask:
    """Tests for PromptCurrentTask model."""

    def test_valid_creation_all_fields(self):
        """Test creating a valid PromptCurrentTask with all fields."""
        response_obj = TurnResponse(status="success", message="Task completed")
        task = PromptCurrentTask(
            type="user_task",
            instruction="Fix the bug",
            response=response_obj,
            name="fix_bug",
            content="Bug details",
            original_turns_range=[1, 3],
            timestamp="2025-01-01T00:00:00+09:00",
        )
        assert task.type == "user_task"
        assert task.instruction == "Fix the bug"
        assert isinstance(task.response, TurnResponse)
        assert task.response.status == "success"
        assert task.name == "fix_bug"
        assert task.content == "Bug details"
        assert task.original_turns_range == [1, 3]
        assert task.timestamp == "2025-01-01T00:00:00+09:00"

    def test_valid_creation_required_fields_only(self):
        """Test creating a valid PromptCurrentTask with only required fields."""
        task = PromptCurrentTask(
            type="user_task",
            timestamp="2025-01-01T00:00:00+09:00",
        )
        assert task.type == "user_task"
        assert task.timestamp == "2025-01-01T00:00:00+09:00"
        assert task.instruction is None
        assert task.response is None

    def test_creation_with_string_response(self):
        """Test creating a PromptCurrentTask where response is a string."""
        task = PromptCurrentTask(
            type="model_response",
            response="Done",
            timestamp="2025-01-01T00:00:00+09:00",
        )
        assert task.response == "Done"

    def test_validation_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        # Missing timestamp
        with pytest.raises(ValidationError) as exc_info:
            PromptCurrentTask(type="user_task")
        assert "timestamp" in str(exc_info.value)

        # Missing type
        with pytest.raises(ValidationError) as exc_info:
            PromptCurrentTask(timestamp="2025-01-01T00:00:00+09:00")
        assert "type" in str(exc_info.value)

    def test_camel_case_alias_serialization(self):
        """Test that serialization uses camelCase for original_turns_range."""
        task = PromptCurrentTask(
            type="compressed_history",
            original_turns_range=[1, 5],
            timestamp="2025-01-01T00:00:00+09:00",
        )
        # by_alias=True should produce originalTurnsRange
        dumped = task.model_dump(by_alias=True)
        assert "originalTurnsRange" in dumped
        assert dumped["originalTurnsRange"] == [1, 5]
        assert "original_turns_range" not in dumped

        # Without by_alias, it should be snake_case
        dumped_snake = task.model_dump()
        assert "original_turns_range" in dumped_snake
        assert dumped_snake["original_turns_range"] == [1, 5]

    def test_deserialization_from_camel_case(self):
        """Test that the model can be validated from camelCase data."""
        data = {
            "type": "compressed_history",
            "originalTurnsRange": [2, 4],
            "timestamp": "2025-01-01T00:00:00+09:00",
        }
        task = PromptCurrentTask.model_validate(data)
        assert task.original_turns_range == [2, 4]

    def test_roundtrip_serialization(self):
        """Test serialize -> deserialize preserves all data and types."""
        response_obj = TurnResponse(status="error", message="Failed")
        original = PromptCurrentTask(
            type="tool_response",
            name="test_tool",
            response=response_obj,
            original_turns_range=[1, 1],
            timestamp="2025-01-01T00:00:00+09:00",
        )

        # Serialize to JSON string with camelCase
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = PromptCurrentTask.model_validate(data)

        assert restored.type == original.type
        assert restored.name == original.name
        assert isinstance(restored.response, TurnResponse)
        assert restored.response.status == "error"
        assert restored.original_turns_range == original.original_turns_range
        assert restored.timestamp == original.timestamp
