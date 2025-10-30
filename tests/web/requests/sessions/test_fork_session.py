import unittest

from pipe.web.requests.sessions.fork_session import ForkSessionRequest
from pydantic import ValidationError


class TestForkSessionRequest(unittest.TestCase):
    def test_valid_session_id(self):
        """
        Tests that a valid, non-empty session_id passes validation.
        """
        try:
            ForkSessionRequest(session_id="valid_session_id")
        except ValidationError as e:
            self.fail(f"Validation failed unexpectedly: {e}")

    def test_empty_session_id_raises_error(self):
        """
        Tests that an empty session_id string raises a ValueError.
        """
        with self.assertRaises(ValidationError):
            ForkSessionRequest(session_id="")

    def test_whitespace_session_id_raises_error(self):
        """
        Tests that a session_id containing only whitespace raises a ValueError.
        """
        with self.assertRaises(ValidationError):
            ForkSessionRequest(session_id="   ")


if __name__ == "__main__":
    unittest.main()
