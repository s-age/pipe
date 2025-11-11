import unittest

from pipe.web.requests.sessions.edit_turn import EditTurnRequest
from pydantic import ValidationError


class TestEditTurnRequest(unittest.TestCase):
    def test_valid_content_is_accepted(self):
        """Tests that valid content passes validation."""
        request_data = {"content": "This is valid content."}
        try:
            edit_request = EditTurnRequest(**request_data)
            self.assertEqual(edit_request.content, "This is valid content.")
            self.assertIsNone(edit_request.instruction)
        except Exception as e:
            self.fail(f"EditTurnRequest validation failed unexpectedly: {e}")

    def test_valid_instruction_is_accepted(self):
        """Tests that valid instruction passes validation."""
        request_data = {"instruction": "This is a valid instruction."}
        try:
            edit_request = EditTurnRequest(**request_data)
            self.assertEqual(edit_request.instruction, "This is a valid instruction.")
            self.assertIsNone(edit_request.content)
        except Exception as e:
            self.fail(f"EditTurnRequest validation failed unexpectedly: {e}")

    def test_empty_content_raises_error(self):
        """Tests that empty content fails validation."""
        request_data = {"content": ""}
        with self.assertRaises(ValidationError) as context:
            EditTurnRequest(**request_data)
        self.assertIn("cannot be empty", str(context.exception).lower())

    def test_whitespace_only_content_raises_error(self):
        """Tests that whitespace-only content fails validation."""
        request_data = {"content": "   \n\t  "}
        with self.assertRaises(ValidationError) as context:
            EditTurnRequest(**request_data)
        self.assertIn("cannot be empty", str(context.exception).lower())

    def test_empty_instruction_raises_error(self):
        """Tests that empty instruction fails validation."""
        request_data = {"instruction": ""}
        with self.assertRaises(ValidationError) as context:
            EditTurnRequest(**request_data)
        self.assertIn("cannot be empty", str(context.exception).lower())

    def test_whitespace_only_instruction_raises_error(self):
        """Tests that whitespace-only instruction fails validation."""
        request_data = {"instruction": "   "}
        with self.assertRaises(ValidationError) as context:
            EditTurnRequest(**request_data)
        self.assertIn("cannot be empty", str(context.exception).lower())

    def test_model_dump_excludes_none_values(self):
        """Tests that model_dump only includes non-None fields."""
        request_data = {"content": "Some content"}
        edit_request = EditTurnRequest(**request_data)
        dumped = edit_request.model_dump()
        self.assertIn("content", dumped)
        self.assertNotIn("instruction", dumped)

    def test_both_fields_can_be_provided(self):
        """Tests that both content and instruction can be provided together."""
        request_data = {"content": "Content", "instruction": "Instruction"}
        try:
            edit_request = EditTurnRequest(**request_data)
            self.assertEqual(edit_request.content, "Content")
            self.assertEqual(edit_request.instruction, "Instruction")
        except Exception as e:
            self.fail(f"EditTurnRequest validation failed unexpectedly: {e}")


if __name__ == "__main__":
    unittest.main()
