import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.factories.service_factory import ServiceFactory
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
        self.service_factory = ServiceFactory(self.project_root, self.settings)
        self.session_service = self.service_factory.create_session_service()
        self.todo_service = self.service_factory.create_session_todo_service()

        session = self.session_service.create_new_session("Test", "Test", [])
        self.session_id = session.session_id

        # Add some initial todos to the session
        initial_todos = [
            TodoItem(title="Task 1", checked=False),
            TodoItem(title="Task 2", checked=True),
        ]
        self.todo_service.update_todos(
            self.session_id, initial_todos
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

    def test_delete_todos_no_session_service(self):
        """
        Tests that an error is returned if session_service is not provided.
        """
        result = delete_todos(session_id=self.session_id)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "This tool requires an active session.")

    def test_delete_todos_failure(self):
        """
        Tests that the tool returns an error if the session_service raises an
        exception.
        """
        mock_session_service = MagicMock(spec=SessionService)
        mock_session = MagicMock()
        mock_session_service.get_session.return_value = mock_session
        error_message = "Test exception"

        with patch(
            "pipe.core.domains.todos.delete_todos_in_session",
            side_effect=Exception(error_message),
        ) as mock_delete_todos_in_session:
            result = delete_todos(
                session_service=mock_session_service, session_id=self.session_id
            )

            mock_delete_todos_in_session.assert_called_once_with(mock_session)
            self.assertIn("error", result)
            self.assertEqual(
                result["error"], f"Failed to delete todos from session: {error_message}"
            )


if __name__ == "__main__":
    unittest.main()
