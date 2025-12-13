import json
import os
import sys
import unittest
import warnings

import yaml
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.models.todo import TodoItem
from pipe.core.tools.delete_todos import delete_todos
from pipe.core.tools.edit_todos import edit_todos

# Suppress Pydantic UserWarning about shadowed attributes
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Ensure src is in path
sys.path.append(os.path.abspath("src"))


class TestTodoTools(unittest.TestCase):
    def setUp(self):
        self.project_root = os.getcwd()

        # Load settings
        with open("setting.default.yml") as f:
            settings_data = yaml.safe_load(f)
        self.settings = Settings(**settings_data)

        self.factory = ServiceFactory(self.project_root, self.settings)
        self.session_service = self.factory.create_session_service()

        # Create temp session
        self.session_id = "test_todo_tools_session"
        self.sessions_dir = os.path.join(self.project_root, self.settings.sessions_path)
        os.makedirs(self.sessions_dir, exist_ok=True)

        self.session_file = os.path.join(self.sessions_dir, f"{self.session_id}.json")

        # Initial session data
        initial_data = {
            "session_id": self.session_id,
            "created_at": "2023-01-01T00:00:00Z",
            "purpose": "Test Todo Tools",
            "background": "Testing",
            "roles": [],
            "turns": [],
            "todos": [],
            "references": [],
            "pools": [],
            "multi_step_reasoning_enabled": False,
            "token_count": 0,
            "artifacts": [],
            "procedure": None,
            "hyperparameters": {"temperature": 0.5, "top_p": 0.9, "top_k": 40},
        }

        with open(self.session_file, "w") as f:
            json.dump(initial_data, f)

    def tearDown(self):
        # Clean up
        if os.path.exists(self.session_file):
            os.remove(self.session_file)

    def test_edit_todos(self):
        todos = [
            TodoItem(title="Test Task 1", description="Desc 1", checked=False),
            TodoItem(title="Test Task 2", description="Desc 2", checked=True),
        ]

        result = edit_todos(
            todos, session_service=self.session_service, session_id=self.session_id
        )

        self.assertIn("message", result)
        self.assertIn("successfully updated", result["message"])

        # Verify
        session = self.session_service.get_session(self.session_id)
        if session is None:
            self.fail("Session loaded as None")

        self.assertEqual(len(session.todos), 2)
        self.assertEqual(session.todos[0].title, "Test Task 1")
        self.assertTrue(session.todos[1].checked)

    def test_delete_todos(self):
        # Setup existing todos
        todos = [TodoItem(title="Task to delete", description="", checked=False)]
        edit_todos(
            todos, session_service=self.session_service, session_id=self.session_id
        )

        # Action
        result = delete_todos(
            session_service=self.session_service, session_id=self.session_id
        )

        self.assertIn("message", result)
        self.assertIn("successfully deleted", result["message"])

        # Verify
        session = self.session_service.get_session(self.session_id)
        # Session.todos can be None or empty list
        self.assertTrue(session.todos is None or len(session.todos) == 0)


if __name__ == "__main__":
    unittest.main()
