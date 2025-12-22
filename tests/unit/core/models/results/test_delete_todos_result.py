"""Tests for DeleteTodosResult model."""

import json

from pipe.core.models.results.delete_todos_result import DeleteTodosResult

from tests.helpers.results_factory import ResultFactory
from tests.helpers.todo_factory import TodoFactory


class TestDeleteTodosResult:
    """DeleteTodosResult model validation and serialization tests."""

    def test_default_values(self):
        """Test creating a DeleteTodosResult with default values."""
        result = DeleteTodosResult()
        assert result.message is None
        assert result.current_todos is None
        assert result.error is None

    def test_valid_creation(self):
        """Test creating a DeleteTodosResult with explicit values using factory."""
        message = "2 todos deleted"
        current_todos = TodoFactory.create_batch(3)
        result = ResultFactory.create_delete_todos_result(
            message=message, current_todos=current_todos
        )
        assert result.message == message
        assert len(result.current_todos) == 3
        assert result.current_todos[0].title == "Test Todo 0"
        assert result.error is None

    def test_error_creation(self):
        """Test creating a DeleteTodosResult with an error message."""
        error_msg = "Failed to delete todos"
        result = ResultFactory.create_delete_todos_result(message=None, error=error_msg)
        assert result.message is None
        assert result.error == error_msg

    def test_serialization_with_aliases(self):
        """Test serialization with by_alias=True for camelCase conversion."""
        current_todos = TodoFactory.create_batch(1)
        result = ResultFactory.create_delete_todos_result(
            message="Success", current_todos=current_todos
        )

        # CamelCaseModel should convert current_todos to currentTodos
        dumped = result.model_dump(by_alias=True)
        assert dumped["message"] == "Success"
        assert "currentTodos" in dumped
        assert len(dumped["currentTodos"]) == 1
        assert dumped["currentTodos"][0]["title"] == "Test Todo 0"

    def test_deserialization(self):
        """Test that model_validate works correctly from a dictionary."""
        data = {
            "message": "Deleted",
            "currentTodos": [{"title": "Remaining Task", "checked": False}],
            "error": None,
        }
        result = DeleteTodosResult.model_validate(data)
        assert result.message == "Deleted"
        assert len(result.current_todos) == 1
        assert result.current_todos[0].title == "Remaining Task"

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization preserve data."""
        original = ResultFactory.create_delete_todos_result(
            message="Batch delete completed", current_todos=TodoFactory.create_batch(2)
        )

        # Serialize to JSON string (by_alias=True for consistency with API)
        json_str = original.model_dump_json(by_alias=True)

        # Deserialize back
        data = json.loads(json_str)
        restored = DeleteTodosResult.model_validate(data)

        # Verify all fields are preserved
        assert restored.message == original.message
        assert len(restored.current_todos) == len(original.current_todos)
        assert restored.current_todos[0].title == original.current_todos[0].title
        assert restored.error == original.error
        assert restored == original
