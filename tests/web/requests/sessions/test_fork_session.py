import unittest
from unittest.mock import Mock, patch

from pipe.core.models.session import Session
from pipe.core.models.turn import ModelResponseTurn
from pipe.web.requests.sessions.fork_session import ForkSessionRequest
from pydantic import ValidationError


class TestForkSessionRequest(unittest.TestCase):
    def setUp(self):
        """Set up mock session with multiple turns for fork validation."""
        self.mock_session = Session(
            session_id="test_session",
            created_at="2024-01-01T00:00:00Z",
            roles=[],
            turns=[
                ModelResponseTurn(
                    type="model_response",
                    content="Turn 0",
                    timestamp="2024-01-01T00:00:00Z",
                ),
                ModelResponseTurn(
                    type="model_response",
                    content="Turn 1",
                    timestamp="2024-01-01T00:00:01Z",
                ),
                ModelResponseTurn(
                    type="model_response",
                    content="Turn 2",
                    timestamp="2024-01-01T00:00:02Z",
                ),
            ]
        )

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_session_id(self, mock_get_service):
        """
        Tests a valid session_id with valid fork_index passes.
        """
        mock_service = Mock()
        mock_service.get_session.return_value = self.mock_session
        mock_get_service.return_value = mock_service

        try:
            ForkSessionRequest(session_id="valid_session_id", fork_index=1)
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
