import os
import shutil
import tempfile
import unittest

from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings
from pipe.core.models.todo import TodoItem
from pipe.core.models.turn import ModelResponseTurn
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService


class TestPromptService(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        # Create necessary subdirectories for services
        os.makedirs(os.path.join(self.project_root, "sessions"))
        os.makedirs(os.path.join(self.project_root, "roles"))  # For RoleCollection

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
        self.prompt_service = PromptService(project_root=self.project_root)

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_build_prompt_basic_structure(self):
        """Tests that the basic structure of the Prompt object is correct."""
        args = TaktArgs(
            purpose="Test Purpose", background="Test BG", instruction="Test Instruction"
        )
        self.session_service.prepare_session_for_takt(args)

        prompt = self.prompt_service.build_prompt(self.session_service)

        expected_description = (
            "This structured prompt guides your response. First, understand the "
            "core instructions: `main_instruction` defines your thinking "
            "process. Next, identify the immediate objective from `current_task` "
            "and `todos`. Then, gather all context required to execute the task "
            "by processing `session_goal`, `roles`, `constraints`, "
            "`conversation_history`, and `file_references` in that order. "
            "Finally, execute the `current_task` by synthesizing all gathered "
            "information."
        )
        self.assertEqual(prompt.description, expected_description)
        self.assertEqual(prompt.session_goal.purpose, "Test Purpose")
        self.assertEqual(prompt.session_goal.background, "Test BG")
        self.assertEqual(prompt.current_task.instruction, "Test Instruction")
        self.assertEqual(len(prompt.conversation_history.turns), 0)

    def test_build_prompt_with_history(self):
        """Tests that conversation history is correctly populated."""
        args = TaktArgs(
            purpose="Test", background="Test", instruction="Third instruction"
        )
        self.session_service.prepare_session_for_takt(args)
        session_id = self.session_service.current_session_id

        # Manually add older turns to simulate a history
        session = self.session_service.get_session(session_id)
        session.turns.insert(
            0,
            ModelResponseTurn(
                type="model_response", content="Response to first", timestamp="..."
            ),
        )
        session.turns.insert(
            0, TaktArgs(instruction="First instruction").to_turn("...")
        )  # Simulate another user turn
        self.session_service._save_session(session)
        self.session_service.current_session = self.session_service.get_session(
            session_id
        )

        prompt = self.prompt_service.build_prompt(self.session_service)

        self.assertEqual(len(prompt.conversation_history.turns), 2)
        self.assertEqual(
            prompt.conversation_history.turns[0]["instruction"], "First instruction"
        )
        self.assertEqual(
            prompt.conversation_history.turns[1]["content"], "Response to first"
        )
        self.assertEqual(prompt.current_task.instruction, "Third instruction")

    def test_build_prompt_with_references_and_todos(self):
        """Tests that file references and todos are correctly included."""
        # Create a dummy file to be referenced
        ref_file_path = os.path.join(self.project_root, "ref.txt")
        with open(ref_file_path, "w") as f:
            f.write("reference content")

        args = TaktArgs(
            purpose="Test",
            background="Test",
            instruction="Test",
            references=["ref.txt"],
        )
        self.session_service.prepare_session_for_takt(args)
        session_id = self.session_service.current_session_id

        # Add todos
        todos = [TodoItem(title="My Todo", checked=False)]
        self.session_service.update_todos(session_id, todos)
        self.session_service.current_session = self.session_service.get_session(
            session_id
        )

        prompt = self.prompt_service.build_prompt(self.session_service)

        self.assertIsNotNone(prompt.file_references)
        self.assertEqual(len(prompt.file_references), 1)
        self.assertEqual(prompt.file_references[0].path, "ref.txt")
        self.assertEqual(prompt.file_references[0].content, "reference content")

        self.assertIsNotNone(prompt.todos)
        self.assertEqual(len(prompt.todos), 1)
        self.assertEqual(prompt.todos[0].title, "My Todo")

    def test_build_prompt_multi_step_reasoning(self):
        """
        Tests that the multi_step_reasoning flag correctly affects the prompt.
        """
        # Case 1: multi_step_reasoning is enabled
        args_enabled = TaktArgs(
            purpose="Test",
            background="Test",
            instruction="Test",
            multi_step_reasoning=True,
        )
        self.session_service.prepare_session_for_takt(args_enabled)
        prompt_enabled = self.prompt_service.build_prompt(self.session_service)

        self.assertTrue(
            prompt_enabled.constraints.processing_config.multi_step_reasoning_active
        )
        self.assertIsNotNone(prompt_enabled.reasoning_process)

        # Case 2: multi_step_reasoning is disabled (default)
        args_disabled = TaktArgs(
            purpose="Test",
            background="Test",
            instruction="Test",
            multi_step_reasoning=False,
        )
        self.session_service.prepare_session_for_takt(args_disabled)
        prompt_disabled = self.prompt_service.build_prompt(self.session_service)

        self.assertFalse(
            prompt_disabled.constraints.processing_config.multi_step_reasoning_active
        )
        self.assertIsNone(prompt_disabled.reasoning_process)

    def test_build_prompt_continuing_session(self):
        """Tests prompt generation when continuing an existing session."""
        # 1. Create an initial session
        args1 = TaktArgs(purpose="Initial", background="BG", instruction="First task")
        self.session_service.prepare_session_for_takt(args1)
        session_id = self.session_service.current_session_id

        # 2. Continue the session with a new instruction
        args2 = TaktArgs(session=session_id, instruction="Second task")
        self.session_service.prepare_session_for_takt(args2)

        prompt = self.prompt_service.build_prompt(self.session_service)

        self.assertEqual(prompt.session_goal.purpose, "Initial")  # Purpose is retained
        self.assertEqual(prompt.current_task.instruction, "Second task")
        self.assertEqual(len(prompt.conversation_history.turns), 1)
        self.assertEqual(
            prompt.conversation_history.turns[0]["instruction"], "First task"
        )

    def test_build_prompt_after_fork(self):
        """Tests prompt generation for a forked session."""
        # 1. Create a session with a few turns
        args1 = TaktArgs(purpose="Original", background="BG", instruction="First")
        self.session_service.prepare_session_for_takt(args1)
        session_id = self.session_service.current_session_id

        session = self.session_service.get_session(session_id)
        session.turns.append(
            ModelResponseTurn(
                type="model_response", content="First response", timestamp="..."
            )
        )
        session.turns.append(TaktArgs(instruction="Second").to_turn("..."))
        self.session_service._save_session(session)

        # 2. Fork the session at the first model response (turn index 1)
        forked_session_id = self.session_service.fork_session(session_id, fork_index=1)

        # 3. Continue the forked session
        args_fork = TaktArgs(session=forked_session_id, instruction="New task for fork")
        self.session_service.prepare_session_for_takt(args_fork)

        prompt = self.prompt_service.build_prompt(self.session_service)

        self.assertTrue(prompt.session_goal.purpose.startswith("Fork of: Original"))
        self.assertEqual(prompt.current_task.instruction, "New task for fork")
        # History should contain turns up to the fork point
        self.assertEqual(len(prompt.conversation_history.turns), 2)
        self.assertEqual(prompt.conversation_history.turns[0]["instruction"], "First")
        self.assertEqual(
            prompt.conversation_history.turns[1]["content"], "First response"
        )

    def test_build_prompt_property_order(self):
        """Tests that the prompt properties are in the correct logical (cognitive)
        order."""
        # Setup a session with all optional components to ensure they are ordered
        # correctly
        ref_file_path = os.path.join(self.project_root, "ref.txt")
        with open(ref_file_path, "w") as f:
            f.write("ref content")
        args = TaktArgs(
            purpose="Test Order",
            background="BG",
            instruction="Test Instruction",
            references=["ref.txt"],
            multi_step_reasoning=True,
        )
        self.session_service.prepare_session_for_takt(args)
        session_id = self.session_service.current_session_id
        todos = [TodoItem(title="My Todo", checked=False)]
        self.session_service.update_todos(session_id, todos)
        self.session_service.current_session = self.session_service.get_session(
            session_id
        )

        prompt = self.prompt_service.build_prompt(self.session_service)

        # Pydantic's model_dump preserves field order from the model definition
        prompt_dict = prompt.model_dump(exclude_none=True)
        actual_order = list(prompt_dict.keys())

        expected_order = [
            "description",
            "main_instruction",
            "reasoning_process",
            "current_task",
            "todos",
            "current_datetime",
            "session_goal",
            "roles",
            "constraints",
            "conversation_history",
            "file_references",
        ]

        self.assertEqual(actual_order, expected_order)


if __name__ == "__main__":
    unittest.main()
