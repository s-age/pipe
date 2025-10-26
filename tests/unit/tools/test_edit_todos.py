import unittest
import os
import tempfile
import shutil

from pipe.core.tools.edit_todos import edit_todos
from pipe.core.services.session_service import SessionService
from pipe.core.models.settings import Settings

class TestEditTodosTool(unittest.TestCase):

    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        settings_data = {
            "model": "test-model", "search_model": "test-model", "context_limit": 10000,
            "api_mode": "gemini-api", "language": "en", "yolo": False, "expert_mode": False, "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"}
            }
        }
        self.settings = Settings(**settings_data)
        self.session_service = SessionService(project_root=self.project_root, settings=self.settings)
        self.session_id = self.session_service.create_new_session("Test", "Test", [])

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_edit_todos_updates_session_todos(self):
        """
        Tests that the edit_todos tool correctly updates the todos in the session.
        """
        new_todos = [
            {"title": "New Task 1", "description": "Desc 1", "checked": False},
            {"title": "New Task 2", "description": "Desc 2", "checked": True},
        ]
        
        result = edit_todos(
            todos=new_todos,
            session_service=self.session_service,
            session_id=self.session_id
        )

        self.assertIn("message", result)
        self.assertNotIn("error", result)

        # Verify that the todos were actually updated
        session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(session.todos), 2)
        self.assertEqual(session.todos[0].title, "New Task 1")
        self.assertTrue(session.todos[1].checked)

if __name__ == '__main__':
    unittest.main()
