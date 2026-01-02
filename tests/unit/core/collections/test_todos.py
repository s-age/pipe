"""Unit tests for TodoCollection."""

from pipe.core.collections.todos import TodoCollection
from pipe.core.models.todo import TodoItem

from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.todo_factory import TodoFactory


class TestTodoCollection:
    """Tests for TodoCollection class."""

    def test_init_with_none(self):
        """Test initialization with None."""
        collection = TodoCollection(None)
        assert collection._todos == []

    def test_init_with_list(self):
        """Test initialization with a list of TodoItem objects."""
        todos = TodoFactory.create_batch(3)
        collection = TodoCollection(todos)
        assert collection._todos == todos
        assert len(collection._todos) == 3

    def test_update_in_session_with_dicts(self):
        """Test updating todos in a session using dictionaries."""
        session = SessionFactory.create()
        todos_data = [
            {"title": "Task 1", "description": "Desc 1", "checked": False},
            {"title": "Task 2", "description": "Desc 2", "checked": True},
        ]

        TodoCollection.update_in_session(session, todos_data)

        assert len(session.todos) == 2
        assert isinstance(session.todos[0], TodoItem)
        assert session.todos[0].title == "Task 1"
        assert session.todos[1].checked is True

    def test_update_in_session_with_items(self):
        """Test updating todos in a session using TodoItem objects."""
        session = SessionFactory.create()
        todos = TodoFactory.create_batch(2)

        TodoCollection.update_in_session(session, todos)

        assert len(session.todos) == 2
        assert session.todos == todos

    def test_delete_in_session(self):
        """Test deleting todos from a session."""
        todos = TodoFactory.create_batch(2)
        session = SessionFactory.create(todos=todos)
        assert session.todos is not None

        TodoCollection.delete_in_session(session)

        assert session.todos is None

    def test_get_for_prompt(self):
        """Test getting todos formatted for a prompt."""
        todos = [
            TodoFactory.create(title="Task 1", checked=False),
            TodoFactory.create(title="Task 2", checked=True),
        ]
        collection = TodoCollection(todos)

        result = collection.get_for_prompt()

        assert len(result) == 2
        assert isinstance(result[0], dict)
        assert result[0]["title"] == "Task 1"
        assert result[0]["checked"] is False
        assert result[1]["title"] == "Task 2"
        assert result[1]["checked"] is True
