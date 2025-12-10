import unittest
from unittest.mock import Mock, patch

from pipe.core.models.session import Session
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest
from pydantic import ValidationError


class TestSendInstructionRequest(unittest.TestCase):
    def setUp(self):
        """Set up mock session with empty pools for capacity validation."""
        self.mock_session = Session(
            session_id="test_session",
            created_at="2024-01-01T00:00:00Z",
            roles=[],
            turns=[],
            pools=[],
        )

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_instruction(self, mock_get_service):
        """
        Tests that a valid, non-empty instruction passes validation.
        """
        mock_service = Mock()
        mock_service.get_session.return_value = self.mock_session
        mock_get_service.return_value = mock_service

        try:
            SendInstructionRequest.create_with_path_params(
                path_params={"session_id": "test_session"},
                body_data={"instruction": "This is a valid instruction."},
            )
        except ValidationError as e:
            self.fail(f"Validation failed unexpectedly: {e}")

    def test_empty_instruction_raises_error(self):
        """
        Tests that an empty instruction string raises a ValueError.
        """
        with self.assertRaises(ValidationError):
            SendInstructionRequest.create_with_path_params(
                path_params={"session_id": "test_session"},
                body_data={"instruction": ""},
            )

    def test_whitespace_instruction_raises_error(self):
        """
        Tests that an instruction containing only whitespace raises a ValueError.
        """
        with self.assertRaises(ValidationError):
            SendInstructionRequest.create_with_path_params(
                path_params={"session_id": "test_session"},
                body_data={"instruction": "   "},
            )


if __name__ == "__main__":
    unittest.main()
