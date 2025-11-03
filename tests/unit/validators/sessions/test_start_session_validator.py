import unittest

from pipe.core.validators.sessions import start_session as start_session_validator


class TestStartSessionValidator(unittest.TestCase):
    def test_valid_inputs(self):
        """
        Tests that valid purpose and background pass validation.
        """
        try:
            start_session_validator.validate(
                purpose="Valid purpose", background="Valid background"
            )
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")

    def test_none_purpose_raises_error(self):
        """
        Tests that a None purpose raises a ValueError.
        """
        with self.assertRaises(ValueError) as cm:
                        start_session_validator.validate(
                            purpose=None, background="Valid background"
                        )
        self.assertEqual(str(cm.exception), "Purpose is required for a new session.")

    def test_empty_purpose_raises_error(self):
        """
        Tests that an empty purpose string raises a ValueError.
        """
        with self.assertRaises(ValueError) as cm:
            start_session_validator.validate(purpose="", background="Valid background")
        self.assertEqual(str(cm.exception), "Purpose is required for a new session.")

    def test_none_background_raises_error(self):
        """
        Tests that a None background raises a ValueError.
        """
        with self.assertRaises(ValueError) as cm:
            start_session_validator.validate(purpose="Valid purpose", background=None)
        self.assertEqual(str(cm.exception), "Background is required for a new session.")

    def test_empty_background_raises_error(self):
        """
        Tests that an empty background string raises a ValueError.
        """
        with self.assertRaises(ValueError) as cm:
            start_session_validator.validate(purpose="Valid purpose", background="")
        self.assertEqual(str(cm.exception), "Background is required for a new session.")


if __name__ == "__main__":
    unittest.main()
