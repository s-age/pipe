import unittest
from unittest.mock import Mock

from pipe.core.collections.todos import TodoCollection
from pipe.core.models.todo import TodoItem


class TestTodoCollection(unittest.TestCase):
    def test_get_for_prompt_with_valid_todos(self):
        """
        Tests that get_for_prompt correctly converts a list of TodoItem objects
        into a list of dictionaries.
        """
        todos = [
            TodoItem(
                title="Implement feature X", description="Details for X", checked=False
            ),
            TodoItem(title="Fix bug Y", description="Details for Y", checked=True),
        ]
        collection = TodoCollection(todos)

        prompt_data = collection.get_for_prompt()

        self.assertEqual(len(prompt_data), 2)
        self.assertEqual(prompt_data[0]["title"], "Implement feature X")
        self.assertEqual(prompt_data[0]["checked"], False)
        self.assertEqual(prompt_data[1]["title"], "Fix bug Y")
        self.assertEqual(prompt_data[1]["checked"], True)

    def test_get_for_prompt_with_empty_list(self):
        """
        Tests that get_for_prompt returns an empty list when initialized with an
        empty list.
        """
        collection = TodoCollection([])
        prompt_data = collection.get_for_prompt()
        self.assertEqual(len(prompt_data), 0)

    def test_get_for_prompt_with_none(self):
        """
        Tests that get_for_prompt returns an empty list when initialized with None,
        without raising an error.
        """
        collection = TodoCollection(None)
        prompt_data = collection.get_for_prompt()
        self.assertEqual(len(prompt_data), 0)

    def test_update_in_session(self):
        """
        Tests that the static method update_in_session correctly updates the todos
        on a mock session object.
        """
        mock_session = Mock()
        mock_session.todos = []

        todos_data = [
            {"title": "From dict", "checked": False},
            TodoItem(title="From object", checked=True),
        ]

        TodoCollection.update_in_session(mock_session, todos_data)

        self.assertEqual(len(mock_session.todos), 2)
        self.assertIsInstance(mock_session.todos[0], TodoItem)
        self.assertEqual(mock_session.todos[0].title, "From dict")
        self.assertIsInstance(mock_session.todos[1], TodoItem)
        self.assertEqual(mock_session.todos[1].title, "From object")

    def test_delete_in_session(self):
        """
        Tests that the static method delete_in_session sets the todos attribute
        on a mock session object to None.
        """
        mock_session = Mock()
        mock_session.todos = [TodoItem(title="A todo", checked=False)]

        TodoCollection.delete_in_session(mock_session)

        self.assertIsNone(mock_session.todos)


if __name__ == "__main__":
    unittest.main()
