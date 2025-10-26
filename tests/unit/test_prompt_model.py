import unittest
from pipe.core.models.prompt import Prompt
from pipe.core.models.prompts.constraints import PromptConstraints, PromptHyperparameters, PromptHyperparameter, PromptProcessingConfig
from pipe.core.models.prompts.conversation_history import PromptConversationHistory
from pipe.core.models.prompts.current_task import PromptCurrentTask
from pipe.core.models.prompts.file_reference import PromptFileReference
from pipe.core.models.prompts.roles import PromptRoles
from pipe.core.models.prompts.session_goal import PromptSessionGoal
from pipe.core.models.prompts.todo import PromptTodo

class TestPromptModel(unittest.TestCase):

    def test_full_prompt_creation_from_dict(self):
        """
        Tests that the entire nested Prompt object can be correctly created from a dictionary.
        """
        prompt_data = {
            "current_datetime": "2025-10-27T10:00:00Z",
            "description": "User wants to write a Python script.",
            "session_goal": {
                "description": "Goal description",
                "purpose": "Write a script",
                "background": "To automate a task"
            },
            "roles": {
                "description": "Role definitions",
                "definitions": ["You are a helpful assistant."]
            },
            "constraints": {
                "description": "Constraints for the model",
                "language": "en",
                "processing_config": {
                    "description": "Processing config",
                    "multi_step_reasoning_active": True
                },
                "hyperparameters": {
                    "description": "Hyperparameters",
                    "temperature": {"type": "number", "value": 0.5, "description": "temp"},
                    "top_p": {"type": "number", "value": 0.9, "description": "top_p"},
                    "top_k": {"type": "number", "value": 40, "description": "top_k"}
                }
            },
            "main_instruction": "Your main instruction is to be helpful.",
            "conversation_history": {
                "description": "History of conversation",
                "turns": [{"type": "user_task", "instruction": "Hello", "timestamp": "2025-10-27T09:59:00Z"}]
            },
            "current_task": {
                "type": "user_task",
                "instruction": "Write the script now.",
                "timestamp": "2025-10-27T10:00:00Z"
            },
            "todos": [
                {"title": "Step 1", "description": "Define functions", "checked": False}
            ],
            "file_references": [
                {"path": "main.py", "content": "print('hello')"}
            ],
            "reasoning_process": {"description": "Think step-by-step."}
        }

        prompt = Prompt(**prompt_data)

        # Test top-level fields
        self.assertEqual(prompt.current_datetime, "2025-10-27T10:00:00Z")
        self.assertEqual(prompt.main_instruction, "Your main instruction is to be helpful.")

        # Test nested models
        self.assertIsInstance(prompt.session_goal, PromptSessionGoal)
        self.assertEqual(prompt.session_goal.purpose, "Write a script")

        self.assertIsInstance(prompt.constraints, PromptConstraints)
        self.assertTrue(prompt.constraints.processing_config.multi_step_reasoning_active)
        self.assertEqual(prompt.constraints.hyperparameters.top_k.value, 40)

        self.assertIsInstance(prompt.conversation_history, PromptConversationHistory)
        self.assertEqual(len(prompt.conversation_history.turns), 1)

        self.assertIsInstance(prompt.current_task, PromptCurrentTask)
        self.assertEqual(prompt.current_task.instruction, "Write the script now.")

        self.assertEqual(len(prompt.todos), 1)
        self.assertIsInstance(prompt.todos[0], PromptTodo)
        self.assertEqual(prompt.todos[0].title, "Step 1")

        self.assertEqual(len(prompt.file_references), 1)
        self.assertIsInstance(prompt.file_references[0], PromptFileReference)
        self.assertEqual(prompt.file_references[0].path, "main.py")
        
        self.assertIsNotNone(prompt.reasoning_process)

if __name__ == '__main__':
    unittest.main()
