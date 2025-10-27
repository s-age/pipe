import shutil
import tempfile
import unittest

from pipe.core.models.settings import Settings
from pipe.core.models.todo import TodoItem
from pipe.core.services.session_service import SessionService
from pipe.core.tools.delete_todos import delete_todos


class TestDeleteTodosTool(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        settings_data = {
            "model": "test-model",
            "search_model": "test-model",
            "context_limit": 10000,
            "api_mode": "gemini-api",
            "language": "en",
            "yolo": False,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)
        self.session_service = SessionService(
            project_root=self.project_root, settings=self.settings
        )
        self.session_id = self.session_service.create_new_session("Test", "Test", [])

        # Add some initial todos to the session
        initial_todos = [
            TodoItem(title="Task 1", checked=False),
            TodoItem(title="Task 2", checked=True),
        ]
        self.session_service.update_todos(
            self.session_id, [t.model_dump() for t in initial_todos]
        )

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_delete_todos_clears_session_todos(self):
        """
        Tests that the delete_todos tool correctly sets the session's todos to None.
        """
        # Verify that todos exist before deletion
        session_before = self.session_service.get_session(self.session_id)
        self.assertIsNotNone(session_before.todos)
        self.assertEqual(len(session_before.todos), 2)

        result = delete_todos(
            session_service=self.session_service, session_id=self.session_id
        )

        self.assertIn("message", result)
        self.assertNotIn("error", result)

        # Verify that the todos were actually deleted
        session_after = self.session_service.get_session(self.session_id)
        self.assertIsNone(session_after.todos)


if __name__ == "__main__":
    unittest.main()
