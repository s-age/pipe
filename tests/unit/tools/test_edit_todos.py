import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.models.todo import TodoItem
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

    def test_edit_todos_updates_session_todos(self):
        """
        Tests that the edit_todos tool correctly updates the session's todos.
        """
        new_todos = [
            TodoItem(title="Task 1", checked=True),
            TodoItem(title="Task 3", checked=False),
        ]
        result = edit_todos(
            todos=new_todos,
            session_service=self.session_service,
            session_id=self.session_id,
        )

        self.assertIsNotNone(result.data.message)
        self.assertIsNone(result.data.error)
        self.assertIn("successfully updated", result.data.message)
        self.assertIsNotNone(result.data.current_todos)

        # Verify that the returned todos match the new todos
        self.assertEqual(len(result.data.current_todos), 2)
        self.assertEqual(result.data.current_todos[0].title, "Task 1")
        self.assertTrue(result.data.current_todos[0].checked)
        self.assertEqual(result.data.current_todos[1].title, "Task 3")
        self.assertFalse(result.data.current_todos[1].checked)

        # Optional: Verify actual session state (though tool's return should be
        # sufficient)
        session = self.session_service.get_session(self.session_id)
        self.assertEqual(len(session.todos), 2)
        self.assertEqual(session.todos[0].title, "Task 1")
        self.assertTrue(session.todos[0].checked)
        self.assertEqual(session.todos[1].title, "Task 3")
        self.assertFalse(session.todos[1].checked)

    def test_edit_todos_no_session_service(self):
        """
        Tests that an error is returned if session_service is not provided.
        """
        result = edit_todos(todos=[], session_id=self.session_id)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error, "This tool requires a session_service.")

    def test_edit_todos_failure(self):
        """
        Tests that the tool returns an error if the session_service raises an
        exception.
        """
        mock_session_service = MagicMock(spec=SessionService)
        mock_session = MagicMock()
        mock_session_service.get_session.return_value = mock_session
        error_message = "Test exception"

        # Mock the create_session_todo_service method of the ServiceFactory
        with patch(
            "pipe.core.tools.edit_todos.ServiceFactory.create_session_todo_service"
        ) as mock_create_todo_service:
            mock_todo_service = MagicMock(spec_set=self.todo_service)  # Create a mock
            # for SessionTodoService
            mock_create_todo_service.return_value = mock_todo_service

            # Set the side effect on the update_todos method of the mock_todo_service
            mock_todo_service.update_todos.side_effect = Exception(error_message)

            result = edit_todos(
                todos=[],
                session_service=self.session_service,
                session_id=self.session_id,
            )

            mock_create_todo_service.assert_called_once()  # Ensure the factory
            # method was called
            mock_todo_service.update_todos.assert_called_once_with(
                self.session_id, []
            )  # Ensure update_todos was called on the mock service
            self.assertIsNotNone(result.error)
            self.assertEqual(
                result.error, f"Failed to update todos in session: {error_message}"
            )


if __name__ == "__main__":
    unittest.main()
