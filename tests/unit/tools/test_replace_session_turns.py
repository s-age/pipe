import unittest
from unittest.mock import MagicMock

from pipe.core.tools.replace_session_turns import replace_session_turns


class TestReplaceSessionTurnsTool(unittest.TestCase):
    def test_no_session_service(self):
        """
        Tests that an error is returned if session_service is not provided.
        """
        result = replace_session_turns(
            session_id="sid", start_turn=1, end_turn=2, summary="s"
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "This tool requires an active session.")

    def test_replace_turns_success(self):
        """
        Tests that the tool successfully calls the history_manager to replace turns.
        """
        mock_session_service = MagicMock()
        session_id = "test_session"
        start_turn, end_turn = 1, 5
        summary = "This is a summary."

        result = replace_session_turns(
            session_id=session_id,
            start_turn=start_turn,
            end_turn=end_turn,
            summary=summary,
            session_service=mock_session_service,
        )

        mock_session_service.history_manager.replace_turn_range_with_summary.assert_called_once_with(
            session_id, summary, start_turn - 1, end_turn - 1
        )
        self.assertIn("message", result)

    def test_replace_turns_failure(self):
        """
        Tests that the tool returns an error if the history_manager raises an exception.
        """
        mock_session_service = MagicMock()
        session_id = "test_session"
        error_message = "Test exception"
        mock_history_manager = mock_session_service.history_manager
        mock_history_manager.replace_turn_range_with_summary.side_effect = Exception(
            error_message
        )

        result = replace_session_turns(
            session_id=session_id,
            start_turn=1,
            end_turn=5,
            summary="s",
            session_service=mock_session_service,
        )

        self.assertIn("error", result)
        self.assertEqual(
            result["error"],
            f"Failed to replace turns in session {session_id}: {error_message}",
        )


if __name__ == "__main__":
    unittest.main()
