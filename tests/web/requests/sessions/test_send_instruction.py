import unittest

from pipe.web.requests.sessions.send_instruction import SendInstructionRequest
from pydantic import ValidationError


class TestSendInstructionRequest(unittest.TestCase):
    def test_valid_instruction(self):
        """
        Tests that a valid, non-empty instruction passes validation.
        """
        try:
            SendInstructionRequest(instruction="This is a valid instruction.")
        except ValidationError as e:
            self.fail(f"Validation failed unexpectedly: {e}")

    def test_empty_instruction_raises_error(self):
        """
        Tests that an empty instruction string raises a ValueError.
        """
        with self.assertRaises(ValidationError):
            SendInstructionRequest(instruction="")

    def test_whitespace_instruction_raises_error(self):
        """
        Tests that an instruction containing only whitespace raises a ValueError.
        """
        with self.assertRaises(ValidationError):
            SendInstructionRequest(instruction="   ")


if __name__ == "__main__":
    unittest.main()
