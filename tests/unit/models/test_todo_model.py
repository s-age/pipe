import unittest

from pipe.core.models.todo import TodoItem


class TestTodoModel(unittest.TestCase):
    def test_todo_creation_with_all_fields(self):
        """
        Tests that a TodoItem object can be created with all fields specified.
        """
        todo_data = {
            "title": "Finish the report",
            "description": "Include Q3 and Q4 data.",
            "checked": True,
        }
        todo_item = TodoItem(**todo_data)
        self.assertEqual(todo_item.title, "Finish the report")
        self.assertEqual(todo_item.description, "Include Q3 and Q4 data.")
        self.assertTrue(todo_item.checked)

    def test_todo_creation_with_defaults(self):
        """
        Tests that a TodoItem object uses default values for 'description' and 'checked'
        when they are not provided.
        """
        todo_data = {"title": "Deploy to production"}
        todo_item = TodoItem(**todo_data)
        self.assertEqual(todo_item.title, "Deploy to production")
        self.assertEqual(
            todo_item.description,
            "",
            "The 'description' field should default to an empty string",
        )
        self.assertFalse(
            todo_item.checked, "The 'checked' field should default to False"
        )


if __name__ == "__main__":
    unittest.main()
