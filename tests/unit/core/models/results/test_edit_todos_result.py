import json

from pipe.core.models.results.edit_todos_result import EditTodosResult

from tests.helpers.results_factory import ResultFactory
from tests.helpers.todo_factory import TodoFactory


class TestEditTodosResult:
    """Tests for EditTodosResult model."""

    def test_valid_creation_with_defaults(self):
        """Test creating EditTodosResult with default values."""
        result = EditTodosResult()
        assert result.message is None
        assert result.current_todos is None
        assert result.error is None

    def test_valid_creation_with_data(self):
        """Test creating EditTodosResult with message and todos."""
        todos = TodoFactory.create_batch(2)
        result = ResultFactory.create_edit_todos_result(
            message="Updated", current_todos=todos
        )
        assert result.message == "Updated"
        assert len(result.current_todos) == 2
        assert result.current_todos[0].title == "Test Todo 0"
        assert result.error is None

    def test_creation_with_error(self):
        """Test creating EditTodosResult with error message."""
        result = ResultFactory.create_edit_todos_result(
            message=None, current_todos=None, error="Something went wrong"
        )
        assert result.message is None
        assert result.current_todos == []  # Factory defaults to empty list
        assert result.error == "Something went wrong"

    def test_model_dump_with_aliases(self):
        """Test serialization to camelCase using by_alias=True."""
        todos = TodoFactory.create_batch(1)
        result = ResultFactory.create_edit_todos_result(
            message="Success", current_todos=todos
        )

        dumped = result.model_dump(by_alias=True)
        assert dumped["message"] == "Success"
        assert "currentTodos" in dumped
        assert dumped["currentTodos"][0]["title"] == "Test Todo 0"
        assert dumped["error"] is None

    def test_model_validate(self):
        """Test deserialization from dictionary."""
        data = {
            "message": "Validated",
            "currentTodos": [
                {"title": "Todo 1", "description": "Desc 1", "checked": True}
            ],
            "error": None,
        }

        result = EditTodosResult.model_validate(data)
        assert result.message == "Validated"
        assert len(result.current_todos) == 1
        assert result.current_todos[0].title == "Todo 1"
        assert result.current_todos[0].checked is True

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data integrity."""
        original = ResultFactory.create_edit_todos_result(
            message="Roundtrip test",
            current_todos=TodoFactory.create_batch(3),
            error=None,
        )

        # Serialize to JSON string (camelCase)
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = EditTodosResult.model_validate(data)

        assert restored.message == original.message
        assert len(restored.current_todos) == len(original.current_todos)
        assert restored.current_todos[0].title == original.current_todos[0].title
        assert restored.error == original.error
