import pytest
from pipe.core.models.prompts.todo import PromptTodo
from pydantic import ValidationError

from tests.helpers.prompt_todo_factory import PromptTodoFactory


class TestPromptTodoModel:
    """Tests for the PromptTodo model."""

    def test_valid_todo_creation(self):
        """Test creating a valid PromptTodo with all required fields."""
        todo = PromptTodoFactory.create(
            title="Fix bug", description="Fix the authentication bug", checked=True
        )
        assert todo.title == "Fix bug"
        assert todo.description == "Fix the authentication bug"
        assert todo.checked is True

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        # Missing title
        with pytest.raises(ValidationError) as exc_info:
            PromptTodo(description="desc", checked=False)
        assert "title" in str(exc_info.value)

        # Missing description
        with pytest.raises(ValidationError) as exc_info:
            PromptTodo(title="title", checked=False)
        assert "description" in str(exc_info.value)

        # Missing checked
        with pytest.raises(ValidationError) as exc_info:
            PromptTodo(title="title", description="desc")
        assert "checked" in str(exc_info.value)

    def test_model_dump_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        todo = PromptTodoFactory.create(
            title="Test", description="Description", checked=False
        )
        # All fields in PromptTodo are single words, but CamelCaseModel
        # should still work if we had snake_case fields.
        # Let's verify standard dump first.
        dumped = todo.model_dump()
        assert dumped["title"] == "Test"
        assert dumped["description"] == "Description"
        assert dumped["checked"] is False

        # Verify model_dump_json with by_alias (though no snake_case fields here yet)
        json_str = todo.model_dump_json(by_alias=True)
        assert '"title"' in json_str
        assert '"description"' in json_str
        assert '"checked"' in json_str

    def test_model_validate_from_dict(self):
        """Test that model_validate works with a dictionary."""
        data = {
            "title": "Validated Todo",
            "description": "Validated Description",
            "checked": True,
        }
        todo = PromptTodo.model_validate(data)
        assert todo.title == "Validated Todo"
        assert todo.checked is True

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = PromptTodoFactory.create(
            title="Roundtrip", description="Roundtrip description", checked=True
        )

        # Serialize
        dumped = original.model_dump()

        # Deserialize
        restored = PromptTodo.model_validate(dumped)

        assert restored == original
        assert restored.title == "Roundtrip"
        assert restored.description == "Roundtrip description"
        assert restored.checked is True
