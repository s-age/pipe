"""Unit tests for VerificationService."""

import subprocess
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.models.results.verification_result import (
    VerificationError,
    VerificationResult,
)
from pipe.core.models.turn import (
    ModelResponseTurn,
    UserTaskTurn,
)
from pipe.core.services.verification_service import VerificationService


class TestVerificationService(unittest.TestCase):
    """Tests for VerificationService."""

    def setUp(self):
        """Set up test fixtures."""
        self.session_service = MagicMock()
        self.session_turn_service = MagicMock()
        self.takt_agent = MagicMock()
        self.service = VerificationService(
            self.session_service, self.session_turn_service, self.takt_agent
        )

    def test_prepare_verification_turns_session_not_found(self):
        """Test _prepare_verification_turns when session is not found."""
        self.session_service.get_session.return_value = None

        with self.assertRaises(ValueError) as context:
            self.service._prepare_verification_turns("nonexistent_id", 1, 2, "summary")

        self.assertIn("not found", str(context.exception))

    def test_prepare_verification_turns_invalid_indices(self):
        """Test _prepare_verification_turns with out-of-range indices."""
        mock_session = MagicMock()
        mock_turn = UserTaskTurn(
            type="user_task", instruction="test", timestamp="2024-01-01T00:00:00"
        )
        mock_session.turns = [mock_turn]
        self.session_service.get_session.return_value = mock_session

        with self.assertRaises(ValueError) as context:
            self.service._prepare_verification_turns("session_id", 1, 5, "summary")

        self.assertIn("out of range", str(context.exception))

    def test_prepare_verification_turns_success(self):
        """Test _prepare_verification_turns with valid inputs."""
        mock_turn1 = UserTaskTurn(
            type="user_task", instruction="turn1", timestamp="2024-01-01T00:00:00"
        )
        mock_turn2 = UserTaskTurn(
            type="user_task", instruction="turn2", timestamp="2024-01-01T00:00:01"
        )
        mock_turn3 = UserTaskTurn(
            type="user_task", instruction="turn3", timestamp="2024-01-01T00:00:02"
        )

        mock_session = MagicMock()
        mock_session.turns = [mock_turn1, mock_turn2, mock_turn3]
        self.session_service.get_session.return_value = mock_session

        result = self.service._prepare_verification_turns(
            "session_id", 1, 2, "summary text"
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].type, "compressed_history")
        self.assertEqual(result[0].content, "summary text")
        self.assertEqual(result[1], mock_turn3)

    def test_create_verifier_session(self):
        """Test _create_verifier_session."""
        mock_session = MagicMock()
        mock_session.session_id = "verifier_123"
        self.session_service.create_new_session.return_value = mock_session

        turns = [
            UserTaskTurn(
                type="user_task",
                instruction="test",
                timestamp="2024-01-01T00:00:00",
            )
        ]

        result = self.service._create_verifier_session("target_session_id", turns)

        self.assertEqual(result.session_id, "verifier_123")
        self.session_service.create_new_session.assert_called_once_with(
            purpose="Verification of summary for session target_session_id",
            background=(
                "A sub-agent will review a conversation history where a summary has "
                "been inserted. The agent must judge if the summary is a good "
                "replacement and respond with 'Approved:' or 'Rejected:'. "
                "The agent MUST strictly follow the rules in roles/verifier.md: "
                "Always return 'Approved:' or 'Rejected:' as the first line. "
                "If 'Rejected:', you MUST include the checklist and explicit "
                "reasons for each failed item as required by roles/verifier.md."
            ),
            roles=["roles/verifier.md"],
            multi_step_reasoning_enabled=True,
        )

    def test_run_verifier_agent_success(self):
        """Test _run_verifier_agent with successful execution."""
        self.takt_agent.run_existing_session.return_value = ("stdout", "")

        result = self.service._run_verifier_agent(
            "verifier_session_id", "target_session_id", 1, 5
        )

        self.assertEqual(result, ("stdout", ""))
        self.takt_agent.run_existing_session.assert_called_once()

    def test_run_verifier_agent_subprocess_error(self):
        """Test _run_verifier_agent with subprocess error."""
        # Create CalledProcessError with proper parameters (output is bytes)
        error = subprocess.CalledProcessError(returncode=1, cmd="test")
        error.stdout = b"out"
        error.stderr = b"err"
        self.takt_agent.run_existing_session.side_effect = error

        with self.assertRaises(RuntimeError) as context:
            self.service._run_verifier_agent(
                "verifier_session_id", "target_session_id", 1, 5
            )

        self.assertIn("exit code", str(context.exception))

    def test_run_verifier_agent_generic_error(self):
        """Test _run_verifier_agent with generic error."""
        self.takt_agent.run_existing_session.side_effect = Exception("Test error")

        with self.assertRaises(RuntimeError) as context:
            self.service._run_verifier_agent(
                "verifier_session_id", "target_session_id", 1, 5
            )

        self.assertIn("TaktAgent execution failed", str(context.exception))

    def test_parse_verification_result_no_response(self):
        """Test _parse_verification_result when no response is found."""
        mock_session = MagicMock()
        mock_session.turns = []
        self.session_service.get_session.return_value = mock_session

        with self.assertRaises(ValueError) as context:
            self.service._parse_verification_result("verifier_session_id", "summary")

        self.assertIn("No model_response found", str(context.exception))

    def test_parse_verification_result_approved(self):
        """Test _parse_verification_result with approved response."""
        mock_response_turn = ModelResponseTurn(
            type="model_response",
            content="Approved: Please approve the summary.",
            timestamp="2024-01-01T00:00:00",
        )
        mock_session = MagicMock()
        mock_session.turns = [mock_response_turn]
        self.session_service.get_session.return_value = mock_session

        result = self.service._parse_verification_result(
            "verifier_session_id", "test summary"
        )

        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.verification_status, "pending_approval")
        self.assertIn("Please approve the summary", result.verifier_response)
        self.assertIn("test summary", result.verifier_response)

    def test_parse_verification_result_rejected(self):
        """Test _parse_verification_result with rejected response."""
        mock_response_turn = ModelResponseTurn(
            type="model_response",
            content="Rejected: The summary is incomplete.",
            timestamp="2024-01-01T00:00:00",
        )
        mock_session = MagicMock()
        mock_session.turns = [mock_response_turn]
        self.session_service.get_session.return_value = mock_session

        result = self.service._parse_verification_result(
            "verifier_session_id", "test summary"
        )

        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.verification_status, "rejected")
        self.assertIn("Rejected", result.verifier_response)

    def test_parse_verification_result_unexpected_format(self):
        """Test _parse_verification_result with unexpected response format."""
        mock_response_turn = ModelResponseTurn(
            type="model_response",
            content="This is an unexpected response",
            timestamp="2024-01-01T00:00:00",
        )
        mock_session = MagicMock()
        mock_session.turns = [mock_response_turn]
        self.session_service.get_session.return_value = mock_session

        result = self.service._parse_verification_result(
            "verifier_session_id", "test summary"
        )

        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.verification_status, "rejected")
        self.assertIn("not in the expected format", result.verifier_response)

    @patch("sys.stderr")
    def test_verify_summary_success(self, mock_stderr):
        """Test verify_summary with successful verification."""
        # Setup mocks
        mock_turn = UserTaskTurn(
            type="user_task", instruction="test", timestamp="2024-01-01T00:00:00"
        )
        mock_original_session = MagicMock()
        mock_original_session.turns = [mock_turn]

        mock_verifier_session = MagicMock()
        mock_verifier_session.session_id = "verifier_123"

        mock_response_turn = ModelResponseTurn(
            type="model_response",
            content="Approved: Summary is good.",
            timestamp="2024-01-01T00:00:00",
        )
        mock_verifier_session_data = MagicMock()
        mock_verifier_session_data.turns = [mock_response_turn]

        self.session_service.get_session.side_effect = [
            mock_original_session,
            mock_verifier_session_data,
        ]
        self.session_service.create_new_session.return_value = mock_verifier_session
        self.takt_agent.run_existing_session.return_value = ("", "")

        result = self.service.verify_summary("session_id", 1, 1, "test summary")

        self.assertIsInstance(result, VerificationResult)
        self.assertEqual(result.verification_status, "pending_approval")
        self.session_service.delete_session.assert_called_once_with("verifier_123")

    def test_verify_summary_session_not_found(self):
        """Test verify_summary when session is not found."""
        self.session_service.get_session.return_value = None

        result = self.service.verify_summary("nonexistent_id", 1, 1, "summary")

        self.assertIsInstance(result, VerificationError)
        self.assertIn("not found", result.error)

    def test_verify_summary_invalid_indices(self):
        """Test verify_summary with invalid turn indices."""
        mock_session = MagicMock()
        mock_session.turns = [
            UserTaskTurn(
                type="user_task", instruction="test", timestamp="2024-01-01T00:00:00"
            )
        ]
        self.session_service.get_session.return_value = mock_session

        result = self.service.verify_summary("session_id", 1, 5, "summary")

        self.assertIsInstance(result, VerificationError)
        self.assertIn("out of range", result.error)

    @patch("sys.stderr")
    def test_verify_summary_cleanup_on_error(self, mock_stderr):
        """Test that verifier session is deleted even on error."""
        mock_session = MagicMock()
        mock_session.turns = [
            UserTaskTurn(
                type="user_task", instruction="test", timestamp="2024-01-01T00:00:00"
            )
        ]
        mock_verifier_session = MagicMock()
        mock_verifier_session.session_id = "verifier_123"

        self.session_service.get_session.return_value = mock_session
        self.session_service.create_new_session.return_value = mock_verifier_session
        self.takt_agent.run_existing_session.side_effect = Exception("Test error")

        result = self.service.verify_summary("session_id", 1, 1, "summary")

        self.assertIsInstance(result, VerificationError)
        self.session_service.delete_session.assert_called_once_with("verifier_123")


if __name__ == "__main__":
    unittest.main()
