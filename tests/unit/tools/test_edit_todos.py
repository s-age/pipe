import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, Mock

from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_service import SessionService
from pipe.core.tools.edit_todos import edit_todos


class TestEditTodosTool(unittest.TestCase):
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
        self.mock_repository = Mock(spec=SessionRepository)
        self.session_service = SessionService(
            project_root=self.project_root,
            settings=self.settings,
            repository=self.mock_repository,
        )
        session = self.session_service.create_new_session("Test", "Test", [])
        self.session_id = session.session_id

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
            session_id=self.session_id,
        )

        self.assertIn("message", result)
        self.assertNotIn("error", result)

        # Verify that the todos were actually updated
        session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(session.todos), 2)
        self.assertEqual(session.todos[0].title, "New Task 1")
        self.assertTrue(session.todos[1].checked)

    def test_edit_todos_no_session_service(self):
        """
        Tests that an error is returned if session_service is not provided.
        """
        result = edit_todos(todos=[], session_id=self.session_id)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "This tool requires an active session.")

    def test_edit_todos_failure(self):
        """
        Tests that the tool returns an error if the session_service raises an exception.
        """
        mock_session_service = MagicMock()
        error_message = "Test exception"
        mock_session_service.update_todos.side_effect = Exception(error_message)

        result = edit_todos(
            todos=[], session_service=mock_session_service, session_id=self.session_id
        )

        self.assertIn("error", result)
        self.assertEqual(
            result["error"], f"Failed to update todos in session: {error_message}"
        )


if __name__ == "__main__":
    unittest.main()
