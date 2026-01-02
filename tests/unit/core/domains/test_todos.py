from pipe.core.domains.todos import (
    delete_todos_in_session,
    get_todos_for_prompt,
    update_todos_in_session,
)
from pipe.core.models.todo import TodoItem

from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.todo_factory import TodoFactory


class TestUpdateTodosInSession:
    """Tests for update_todos_in_session function."""

    def test_update_todos_with_dicts(self):
        """Test updating todos using a list of dictionaries."""
        session = SessionFactory.create()
        todos_data = [
            {"title": "Task 1", "description": "Desc 1", "checked": True},
            {"title": "Task 2", "checked": False},
        ]

        update_todos_in_session(session, todos_data)

        assert len(session.todos) == 2
        assert isinstance(session.todos[0], TodoItem)
        assert session.todos[0].title == "Task 1"
        assert session.todos[0].description == "Desc 1"
        assert session.todos[0].checked is True
        assert session.todos[1].title == "Task 2"
        assert session.todos[1].description == ""
        assert session.todos[1].checked is False

    def test_update_todos_with_strings(self):
        """Test updating todos using a list of strings."""
        session = SessionFactory.create()
        todos_data = ["Task 1", "Task 2"]

        update_todos_in_session(session, todos_data)

        assert len(session.todos) == 2
        assert all(isinstance(t, TodoItem) for t in session.todos)
        assert session.todos[0].title == "Task 1"
        assert session.todos[1].title == "Task 2"

    def test_update_todos_with_todo_items(self):
        """Test updating todos using a list of TodoItem objects."""
        session = SessionFactory.create()
        todo1 = TodoFactory.create(title="Task 1")
        todo2 = TodoFactory.create(title="Task 2")
        todos_data = [todo1, todo2]

        update_todos_in_session(session, todos_data)

        assert session.todos == [todo1, todo2]

    def test_update_todos_mixed(self):
        """Test updating todos using a mixed list of dicts, strings, and TodoItems."""
        session = SessionFactory.create()
        todo1 = TodoFactory.create(title="Task 1")
        todos_data = [todo1, {"title": "Task 2", "checked": True}, "Task 3"]

        update_todos_in_session(session, todos_data)

        assert len(session.todos) == 3
        assert session.todos[0] == todo1
        assert session.todos[1].title == "Task 2"
        assert session.todos[1].checked is True
        assert session.todos[2].title == "Task 3"

    def test_update_todos_empty(self):
        """Test updating todos with an empty list."""
        session = SessionFactory.create(todos=[TodoFactory.create()])
        update_todos_in_session(session, [])
        assert session.todos == []


class TestDeleteTodosInSession:
    """Tests for delete_todos_in_session function."""

    def test_delete_todos(self):
        """Test deleting all todos from a session."""
        session = SessionFactory.create(todos=[TodoFactory.create()])
        assert session.todos is not None
        assert len(session.todos) == 1

        delete_todos_in_session(session)

        assert session.todos is None


class TestGetTodosForPrompt:
    """Tests for get_todos_for_prompt function."""

    def test_get_todos_for_prompt_with_list(self):
        """Test getting todos for prompt from a list of TodoItems."""
        todos = [
            TodoFactory.create(title="Task 1", checked=True),
            TodoFactory.create(title="Task 2", description="Desc 2"),
        ]

        # Even though the type hint says TodoCollection, the implementation
        # uses iteration, which works for lists.
        result = get_todos_for_prompt(todos)  # type: ignore

        assert len(result) == 2
        assert result[0]["title"] == "Task 1"
        assert result[0]["checked"] is True
        assert result[1]["title"] == "Task 2"
        assert result[1]["description"] == "Desc 2"

    def test_get_todos_for_prompt_empty_list(self):
        """Test getting todos for prompt from an empty list."""
        result = get_todos_for_prompt([])  # type: ignore
        assert result == []

    def test_get_todos_for_prompt_none(self):
        """Test getting todos for prompt from None."""
        result = get_todos_for_prompt(None)  # type: ignore
        assert result == []
