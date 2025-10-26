import unittest
import json
from pipe.core.models.turn import (
    UserTaskTurn,
    ModelResponseTurn,
    FunctionCallingTurn,
    ToolResponseTurn,
    CompressedHistoryTurn
)

class TestTurnModels(unittest.TestCase):

    def test_user_task_turn_creation(self):
        """Tests the creation of a UserTaskTurn."""
        data = {
            "type": "user_task",
            "instruction": "Please help me with this task.",
            "timestamp": "2025-10-26T20:00:00Z"
        }
        turn = UserTaskTurn(**data)
        self.assertEqual(turn.type, "user_task")
        self.assertEqual(turn.instruction, "Please help me with this task.")
        self.assertEqual(turn.timestamp, "2025-10-26T20:00:00Z")

    def test_model_response_turn_creation(self):
        """Tests the creation of a ModelResponseTurn."""
        data = {
            "type": "model_response",
            "content": "Here is the information you requested.",
            "timestamp": "2025-10-26T20:01:00Z"
        }
        turn = ModelResponseTurn(**data)
        self.assertEqual(turn.type, "model_response")
        self.assertEqual(turn.content, "Here is the information you requested.")

    def test_function_calling_turn_creation(self):
        """Tests the creation of a FunctionCallingTurn."""
        func_call_str = json.dumps({"tool_name": "read_file", "args": {"path": "test.txt"}})
        data = {
            "type": "function_calling",
            "response": func_call_str,
            "timestamp": "2025-10-26T20:02:00Z"
        }
        turn = FunctionCallingTurn(**data)
        self.assertEqual(turn.type, "function_calling")
        self.assertEqual(turn.response, func_call_str)

    def test_tool_response_turn_creation(self):
        """Tests the creation of a ToolResponseTurn."""
        tool_response_dict = {"status": "succeeded", "content": "File content here."}
        data = {
            "type": "tool_response",
            "name": "read_file",
            "response": tool_response_dict,
            "timestamp": "2025-10-26T20:03:00Z"
        }
        turn = ToolResponseTurn(**data)
        self.assertEqual(turn.type, "tool_response")
        self.assertEqual(turn.name, "read_file")
        self.assertEqual(turn.response, tool_response_dict)

    def test_compressed_history_turn_creation(self):
        """Tests the creation of a CompressedHistoryTurn."""
        data = {
            "type": "compressed_history",
            "content": "The user asked for help and the model responded.",
            "original_turns_range": [1, 5],
            "timestamp": "2025-10-26T20:04:00Z"
        }
        turn = CompressedHistoryTurn(**data)
        self.assertEqual(turn.type, "compressed_history")
        self.assertEqual(turn.content, "The user asked for help and the model responded.")
        self.assertEqual(turn.original_turns_range, [1, 5])

if __name__ == '__main__':
    unittest.main()
