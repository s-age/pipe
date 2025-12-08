import unittest
from unittest.mock import Mock, patch

from pipe.core.models.session import Session
from pipe.core.models.turn import ModelResponseTurn
from pipe.web.requests.sessions.edit_turn import EditTurnRequest
from pydantic import ValidationError


class TestEditTurnRequest(unittest.TestCase):
    def setUp(self):
        """Set up mock session data for validation tests."""
        self.mock_session = Session(
            session_id="test_session",
            created_at="2024-01-01T00:00:00Z",
            roles=[],
            turns=[
                ModelResponseTurn(
                    type="model_response",
                    content="test content",
                    timestamp="2024-01-01T00:00:00Z",
                )
            ],
        )

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_content_is_accepted(self, mock_get_service):
        """Tests that valid content passes validation."""
        mock_service = Mock()
        mock_service.get_session.return_value = self.mock_session
        mock_get_service.return_value = mock_service

        try:
            edit_request = EditTurnRequest.create_with_path_params(
                path_params={"session_id": "test_session", "turn_index": "0"},
                body_data={"content": "This is valid content."},
            )
            self.assertEqual(edit_request.content, "This is valid content.")
            self.assertIsNone(edit_request.instruction)
        except Exception as e:
            self.fail(f"EditTurnRequest validation failed unexpectedly: {e}")

    @patch("pipe.web.service_container.get_session_service")
    def test_valid_instruction_is_accepted(self, mock_get_service):
        """Tests that valid instruction passes validation."""
        mock_service = Mock()
        mock_service.get_session.return_value = self.mock_session
        mock_get_service.return_value = mock_service

        try:
            edit_request = EditTurnRequest.create_with_path_params(
                path_params={"session_id": "test_session", "turn_index": "0"},
                body_data={"instruction": "This is a valid instruction."},
            )
            self.assertEqual(edit_request.instruction, "This is a valid instruction.")
            self.assertIsNone(edit_request.content)
        except Exception as e:
            self.fail(f"EditTurnRequest validation failed unexpectedly: {e}")

    def test_empty_content_raises_error(self):
        """Tests that empty content fails validation."""
        with self.assertRaises(ValidationError) as context:
            EditTurnRequest.create_with_path_params(
                path_params={"session_id": "test_session", "turn_index": "0"},
                body_data={"content": ""},
            )
        self.assertIn("cannot be empty", str(context.exception).lower())

    def test_whitespace_only_content_raises_error(self):
        """Tests that whitespace-only content fails validation."""
        with self.assertRaises(ValidationError) as context:
            EditTurnRequest.create_with_path_params(
                path_params={"session_id": "test_session", "turn_index": "0"},
                body_data={"content": "   \n\t  "},
            )
        self.assertIn("cannot be empty", str(context.exception).lower())

    def test_empty_instruction_raises_error(self):
        """Tests that empty instruction fails validation."""
        with self.assertRaises(ValidationError) as context:
            EditTurnRequest.create_with_path_params(
                path_params={"session_id": "test_session", "turn_index": "0"},
                body_data={"instruction": ""},
            )
        self.assertIn("cannot be empty", str(context.exception).lower())

    def test_whitespace_only_instruction_raises_error(self):
        """Tests that whitespace-only instruction fails validation."""
        with self.assertRaises(ValidationError) as context:
            EditTurnRequest.create_with_path_params(
                path_params={"session_id": "test_session", "turn_index": "0"},
                body_data={"instruction": "   "},
            )
        self.assertIn("cannot be empty", str(context.exception).lower())

    @patch("pipe.web.service_container.get_session_service")
    def test_model_dump_excludes_none_values(self, mock_get_service):
        """Tests that model_dump only includes non-None fields."""
        mock_service = Mock()
        mock_service.get_session.return_value = self.mock_session
        mock_get_service.return_value = mock_service

        edit_request = EditTurnRequest.create_with_path_params(
            path_params={"session_id": "test_session", "turn_index": "0"},
            body_data={"content": "Some content"},
        )
        dumped = edit_request.model_dump(exclude_none=True)
        self.assertIn("content", dumped)
        self.assertIn("session_id", dumped)
        self.assertIn("turn_index", dumped)

    @patch("pipe.web.service_container.get_session_service")
    def test_both_fields_can_be_provided(self, mock_get_service):
        """Tests that both content and instruction can be provided together."""
        mock_service = Mock()
        mock_service.get_session.return_value = self.mock_session
        mock_get_service.return_value = mock_service

        try:
            edit_request = EditTurnRequest.create_with_path_params(
                path_params={"session_id": "test_session", "turn_index": "0"},
                body_data={"content": "Content", "instruction": "Instruction"},
            )
            self.assertEqual(edit_request.content, "Content")
            self.assertEqual(edit_request.instruction, "Instruction")
        except Exception as e:
            self.fail(f"EditTurnRequest validation failed unexpectedly: {e}")


if __name__ == "__main__":
    unittest.main()
