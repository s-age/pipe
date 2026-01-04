from unittest.mock import patch

import pytest
from pipe.core.models.todo import TodoItem
from pipe.web.requests.sessions.edit_todos import EditTodosRequest
from pydantic import ValidationError


class TestEditTodosRequest:
    """Tests for the EditTodosRequest model."""

    def test_initialization_with_snake_case(self):
        """Test that the request can be initialized using snake_case field names."""
        todos = [
            {"title": "Task 1", "description": "Desc 1", "checked": False},
            {"title": "Task 2", "description": "Desc 2", "checked": True},
        ]
        request = EditTodosRequest(session_id="test-session-123", todos=todos)
        assert request.session_id == "test-session-123"
        assert len(request.todos) == 2
        assert request.todos[0].title == "Task 1"
        assert request.todos[1].checked is True

    def test_initialization_with_camel_case(self):
        """Test that the request can be initialized using camelCase field names."""
        # normalize_keys validator should handle this
        data = {
            "sessionId": "test-session-456",
            "todos": [{"title": "Task 1", "description": "Desc 1", "checked": False}],
        }
        request = EditTodosRequest.model_validate(data)
        assert request.session_id == "test-session-456"
        assert request.todos[0].title == "Task 1"

    @patch("pipe.web.requests.sessions.edit_todos.normalize_camel_case_keys")
    def test_normalize_keys_is_called(self, mock_normalize):
        """Test that normalize_keys validator calls normalize_camel_case_keys."""
        mock_normalize.return_value = {
            "session_id": "mock-session",
            "todos": [{"title": "Mock Task"}],
        }

        data = {"someKey": "someValue"}
        request = EditTodosRequest.model_validate(data)

        assert request.session_id == "mock-session"
        mock_normalize.assert_called_once_with(data)

    def test_missing_session_id_raises_validation_error(self):
        """Test that missing session_id raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTodosRequest(todos=[])

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("session_id",) for error in errors)

    def test_missing_todos_raises_validation_error(self):
        """Test that missing todos raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTodosRequest(session_id="test-session")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("todos",) for error in errors)

    def test_invalid_todo_item_raises_validation_error(self):
        """Test that invalid todo item in the list raises a ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            EditTodosRequest(
                session_id="test-session", todos=[{"description": "Missing title"}]
            )

        errors = exc_info.value.errors()
        # loc should point to the specific item in the list
        assert any("todos" in error["loc"] for error in errors)

    def test_create_with_path_params(self):
        """Test creating request with path parameters and body data."""
        path_params = {"session_id": "path-session-123"}
        body_data = {"todos": [{"title": "Task from body"}]}
        request = EditTodosRequest.create_with_path_params(
            path_params=path_params, body_data=body_data
        )
        assert request.session_id == "path-session-123"
        assert request.todos[0].title == "Task from body"

    def test_serialization(self):
        """Test that model_dump() returns the correct structure."""
        request = EditTodosRequest(
            session_id="test-session", todos=[TodoItem(title="Task 1")]
        )
        dumped = request.model_dump()
        assert dumped["session_id"] == "test-session"
        assert dumped["todos"][0]["title"] == "Task 1"

    def test_forbid_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            EditTodosRequest(
                session_id="test-session", todos=[], extra_field="not_allowed"
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
