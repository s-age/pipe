import unittest

from pipe.core.validators.sessions import instruction as instruction_validator


class TestInstructionValidator(unittest.TestCase):
    def test_valid_instruction(self):
        """
        Tests that a valid instruction passes validation without error.
        """
        try:
            instruction_validator.validate("This is a valid instruction.")
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_none_instruction_raises_error(self):
        """
        Tests that a None instruction raises a ValueError.
        """
        with self.assertRaises(ValueError) as cm:
            instruction_validator.validate(None)
        self.assertEqual(str(cm.exception), "Instruction is required.")

    def test_empty_instruction_raises_error(self):
        """
        Tests that an empty instruction string raises a ValueError.
        """
        with self.assertRaises(ValueError) as cm:
            instruction_validator.validate("")
        self.assertEqual(str(cm.exception), "Instruction is required.")


if __name__ == "__main__":
    unittest.main()
