import unittest
from pipe.core.collections.todos import TodoCollection
from pipe.core.models.todo import TodoItem

class TestTodoCollection(unittest.TestCase):

    def test_get_for_prompt_with_valid_todos(self):
        """
        Tests that get_for_prompt correctly converts a list of TodoItem objects
        into a list of dictionaries.
        """
        todos = [
            TodoItem(title="Implement feature X", description="Details for X", checked=False),
            TodoItem(title="Fix bug Y", description="Details for Y", checked=True)
        ]
        collection = TodoCollection(todos)
        
        prompt_data = collection.get_for_prompt()
        
        self.assertEqual(len(prompt_data), 2)
        self.assertEqual(prompt_data[0]['title'], "Implement feature X")
        self.assertEqual(prompt_data[0]['checked'], False)
        self.assertEqual(prompt_data[1]['title'], "Fix bug Y")
        self.assertEqual(prompt_data[1]['checked'], True)

    def test_get_for_prompt_with_empty_list(self):
        """
        Tests that get_for_prompt returns an empty list when initialized with an empty list.
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

if __name__ == '__main__':
    unittest.main()
