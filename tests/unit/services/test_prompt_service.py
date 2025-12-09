import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock

import pytest
from pipe.core.collections.references import ReferenceCollection
from pipe.core.collections.turns import TurnCollection
from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.args import TaktArgs
from pipe.core.models.hyperparameters import Hyperparameters
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.models.todo import TodoItem
from pipe.core.models.turn import ModelResponseTurn
from pipe.core.repositories.session_repository import SessionRepository


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
            "reference_ttl": 3,
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)
        self.mock_repository = Mock(spec=SessionRepository)
        self.service_factory = ServiceFactory(self.project_root, self.settings)
        self.session_service = self.service_factory.create_session_service()
        self.prompt_service = self.service_factory.create_prompt_service()
        self.workflow_service = self.service_factory.create_session_workflow_service()
        self.todo_service = self.service_factory.create_session_todo_service()

        # Setup mock repository to return a session with valid hyperparameters
        self.mock_session = Mock(spec=Session)
        self.mock_session.session_id = "test_session"
        self.mock_session.purpose = "Test Purpose"
        self.mock_session.background = "Test Background"
        self.mock_session.turns = TurnCollection()
        self.mock_session.references = ReferenceCollection()
        self.mock_session.todos = []
        self.mock_session.roles = []
        self.mock_session.multi_step_reasoning_enabled = False
        self.mock_session.hyperparameters = Hyperparameters()
        self.mock_repository.find.return_value = self.mock_session

    def tearDown(self):
        shutil.rmtree(self.project_root)

    @pytest.mark.skip
    def test_build_prompt_basic_structure(self):
        """Tests that the basic structure of the Prompt object is correct."""
        args = TaktArgs(
            purpose="Test Purpose", background="Test BG", instruction="Test Instruction"
        )
        self.session_service.prepare(args)

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
        # 1. Create a session without an initial instruction
        session = self.session_service.create_new_session(
            purpose="Test", background="Test", roles=[]
        )
        session_id = session.session_id

        # 2. Manually add historical turns in chronological order
        session.turns.append(TaktArgs(instruction="First instruction").to_turn("..."))
        session.turns.append(
            ModelResponseTurn(
                type="model_response", content="Response to first", timestamp="..."
            )
        )
        self.session_service.repository.save(session)

        # Update current session context for the prompt service
        self.session_service.current_session_id = session_id
        self.session_service.current_session = session  # Directly set the session
        self.session_service.current_instruction = (
            "Third instruction"  # Set current instruction
        )

        prompt = self.prompt_service.build_prompt(self.session_service)

        # With current_instruction provided, all turns are included in history
        # (reversed)
        self.assertEqual(len(prompt.conversation_history.turns), 2)
        self.assertEqual(
            prompt.conversation_history.turns[0].content, "Response to first"
        )
        self.assertEqual(
            prompt.conversation_history.turns[1].instruction, "First instruction"
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
        self.session_service.prepare(args)
        self.mock_repository.find.return_value = self.session_service.current_session
        session_id = self.session_service.current_session_id

        # Add todos
        todos = [TodoItem(title="My Todo", checked=False)]
        self.todo_service.update_todos(session_id, todos)
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
        self.session_service.prepare(args_enabled)
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
        self.session_service.prepare(args_disabled)
        prompt_disabled = self.prompt_service.build_prompt(self.session_service)

        self.assertFalse(
            prompt_disabled.constraints.processing_config.multi_step_reasoning_active
        )
        self.assertIsNone(prompt_disabled.reasoning_process)

    def test_build_prompt_continuing_session(self):
        """Tests prompt generation when continuing an existing session."""
        # 1. Create an initial session
        args1 = TaktArgs(purpose="Initial", background="BG", instruction="First task")
        self.session_service.prepare(args1)
        self.mock_repository.find.return_value = self.session_service.current_session
        session_id = self.session_service.current_session_id

        # 2. Continue the session with a new instruction
        args2 = TaktArgs(session=session_id, instruction="Second task")
        self.session_service.prepare(args2)

        prompt = self.prompt_service.build_prompt(self.session_service)

        self.assertEqual(prompt.session_goal.purpose, "Initial")  # Purpose is retained
        self.assertEqual(prompt.current_task.instruction, "Second task")
        # History excludes the last UserTaskTurn which is used as current_task
        self.assertEqual(len(prompt.conversation_history.turns), 1)
        self.assertEqual(prompt.conversation_history.turns[0].instruction, "First task")

    def test_build_prompt_after_fork(self):
        """Tests prompt generation for a forked session."""
        # 1. Create a session with a few turns
        args1 = TaktArgs(purpose="Original", background="BG", instruction="First")
        self.session_service.prepare(args1)
        session_id = self.session_service.current_session_id
        session = self.session_service.current_session

        session.turns.append(
            ModelResponseTurn(
                type="model_response", content="First response", timestamp="..."
            )
        )
        session.turns.append(TaktArgs(instruction="Second").to_turn("..."))

        # Set up a mock repository that simulates saving and finding sessions
        session_map = {session_id: session}

        def mock_find_by_id(sid):
            return session_map.get(sid)

        def mock_save_by_id(s):
            session_map[s.session_id] = s

        self.mock_repository.find.side_effect = mock_find_by_id
        self.mock_repository.save.side_effect = mock_save_by_id

        self.session_service.repository.save(session)

        # 2. Fork the session at the first model response (turn index 1)
        forked_session_id = self.workflow_service.fork_session(session_id, fork_index=1)

        # 3. Continue the forked session
        args_fork = TaktArgs(session=forked_session_id, instruction="New task for fork")
        self.session_service.prepare(args_fork)

        prompt = self.prompt_service.build_prompt(self.session_service)

        self.assertTrue(prompt.session_goal.purpose.startswith("Fork of: Original"))
        self.assertEqual(prompt.current_task.instruction, "New task for fork")
        # History should contain turns from the forked session except the last
        # UserTaskTurn because it matches current_instruction and is used as
        # current_task.
        # Turns are yielded in reverse order by get_turns_for_prompt
        self.assertEqual(len(prompt.conversation_history.turns), 2)
        self.assertEqual(prompt.conversation_history.turns[0].content, "First response")
        self.assertEqual(prompt.conversation_history.turns[1].instruction, "First")

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
        self.session_service.prepare(args)
        self.mock_repository.find.return_value = self.session_service.current_session
        session_id = self.session_service.current_session_id
        todos = [TodoItem(title="My Todo", checked=False)]
        self.todo_service.update_todos(session_id, todos)
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
