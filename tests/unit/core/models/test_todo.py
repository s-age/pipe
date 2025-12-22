import pytest
from pipe.core.models.todo import TodoItem
from pydantic import ValidationError


class TestTodoItem:
    """TodoItem model validation and serialization tests."""

    def test_valid_todo_creation(self):
        """Test creating a valid todo with all fields."""
        todo = TodoItem(title="Task 1", description="Details of task 1", checked=True)
        assert todo.title == "Task 1"
        assert todo.description == "Details of task 1"
        assert todo.checked is True

    def test_todo_defaults(self):
        """Test default values for TodoItem."""
        todo = TodoItem(title="Simple Task")
        assert todo.title == "Simple Task"
        assert todo.description == ""
        assert todo.checked is False

    def test_todo_validation_missing_title(self):
        """Test that missing title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(description="No title")
        assert "title" in str(exc_info.value)

    def test_todo_map_item_to_title(self):
        """Test that 'item' key is correctly mapped to 'title'."""
        # Test with model_validate
        data = {"item": "Mapped Task", "checked": True}
        todo = TodoItem.model_validate(data)
        assert todo.title == "Mapped Task"
        assert todo.checked is True

        # Test with constructor
        # Note: Pydantic V2 model_validator(mode="before") receives a dict of arguments
        # when using the constructor.
        todo_from_const = TodoItem(item="Constructor Task")
        assert todo_from_const.title == "Constructor Task"

    def test_todo_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        todo = TodoItem(title="Task 1", description="Details", checked=False)
        # Use by_alias=True to get camelCase field names (though title doesn't change)
        # description -> description (no change)
        # checked -> checked (no change)
        # Wait, CamelCaseModel uses to_camel which usually converts snake_case to
        # camelCase.
        # title, description, checked don't have underscores, so they remain the same.
        # If I had "is_done", it would be "isDone".

        dumped = todo.model_dump(by_alias=True)
        assert dumped["title"] == "Task 1"
        assert dumped["description"] == "Details"
        assert dumped["checked"] is False

    def test_todo_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        import json

        original = TodoItem(
            title="Roundtrip Task", description="Preserve this", checked=True
        )

        # Serialize to JSON string
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = TodoItem.model_validate(data)

        # Verify all fields are preserved
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.checked == original.checked
