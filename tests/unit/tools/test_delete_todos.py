import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.models.todo import TodoItem
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
        self.todo_service.update_todos(self.session_id, initial_todos)

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
        self.assertIn("current_todos", result)
        self.assertEqual(result["current_todos"], [])

        # Verify that the todos were actually deleted from the session object
        session_after = self.session_service.get_session(self.session_id)
        self.assertIsNone(session_after.todos)

    def test_delete_todos_no_session_service(self):
        """
        Tests that an error is returned if session_service is not provided.
        """
        result = delete_todos(session_id=self.session_id)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "This tool requires a session_service.")

    def test_delete_todos_failure(self):
        """
        Tests that the tool returns an error if the session_service raises an
        exception.
        """
        error_message = "Test exception"

        # Mock the create_session_todo_service method of the ServiceFactory
        with patch(
            "pipe.core.tools.delete_todos.ServiceFactory.create_session_todo_service"
        ) as mock_create_todo_service:
            mock_todo_service = MagicMock(spec_set=self.todo_service)  # Create a mock
            # for SessionTodoService
            mock_create_todo_service.return_value = mock_todo_service

            # Set the side effect on the delete_todos method of the mock_todo_service
            mock_todo_service.delete_todos.side_effect = Exception(error_message)

            result = delete_todos(
                session_service=self.session_service,
                session_id=self.session_id,
            )

            mock_create_todo_service.assert_called_once()  # Ensure the factory
            # method was called
            mock_todo_service.delete_todos.assert_called_once_with(
                self.session_id
            )  # Ensure delete_todos was called on the mock service
            self.assertIn("error", result)
            self.assertEqual(
                result["error"], f"Failed to delete todos from session: {error_message}"
            )


if __name__ == "__main__":
    unittest.main()
