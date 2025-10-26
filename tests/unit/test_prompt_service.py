import unittest
from unittest.mock import patch
import tempfile
import shutil
import os

from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings

class TestPromptServiceIntegration(unittest.TestCase):

    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.project_root, "sessions")
        os.makedirs(self.sessions_dir)

        # Create a dummy reference file that the test will look for
        with open(os.path.join(self.project_root, "test.py"), "w") as f:
            f.write("print('hello from test file')")

        settings_data = {
            "model": "gemini-pro", "search_model": "gemini-pro", "context_limit": 50000,
            "api_mode": "gemini-api", "language": "en", "yolo": False, "expert_mode": False, "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"}
            }
        }
        self.settings = Settings(**settings_data)
        self.session_service = SessionService(project_root=self.project_root, settings=self.settings)
        self.prompt_service = PromptService(project_root=self.project_root)

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_build_prompt_with_real_session_service(self):
        """
        Tests that build_prompt correctly uses a real SessionService instance.
        """
        args = TaktArgs(
            purpose="Test PromptService",
            background="Background info",
            instruction="Do the task",
            references=["test.py"],
            roles=[]
        )
        # This call prepares the session_service's internal state
        self.session_service.prepare_session_for_takt(args)
        
        # Add todos manually for the test
        from pipe.core.models.todo import TodoItem
        self.session_service.update_todos(self.session_service.current_session_id, [
            TodoItem(title="Test todo", checked=False)
        ])
        # We need to refetch the session data after updating it
        self.session_service.current_session = self.session_service.get_session(self.session_service.current_session_id)

        prompt = self.prompt_service.build_prompt(self.session_service)

        # Verification
        expected_description = "This structured prompt guides your response. First, understand the core instructions: `main_instruction` defines your thinking process. Next, identify the immediate objective from `current_task` and `todos`. Then, gather all context required to execute the task by processing `session_goal`, `roles`, `constraints`, `conversation_history`, and `file_references` in that order. Finally, execute the `current_task` by synthesizing all gathered information."
        self.assertEqual(prompt.description, expected_description)
        self.assertEqual(prompt.session_goal.purpose, "Test PromptService")
        self.assertEqual(prompt.current_task.instruction, "Do the task")
        self.assertEqual(len(prompt.file_references), 1)
        self.assertEqual(prompt.file_references[0].path, "test.py")
        self.assertEqual(len(prompt.todos), 1)
        self.assertEqual(prompt.todos[0].title, "Test todo")

if __name__ == '__main__':
    unittest.main()
