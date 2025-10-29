import unittest
from unittest.mock import MagicMock

from pipe.core.tools.delete_session import delete_session


class TestDeleteSessionTool(unittest.TestCase):
    def test_no_session_service(self):
        """
        Tests that an error is returned if session_service is not provided.
        """
        result = delete_session(session_id="some_id")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "This tool requires a session_service.")

    def test_delete_session_success(self):
        """
        Tests that the tool successfully calls the session_service to delete a session.
        """
        mock_session_service = MagicMock()
        session_id = "session_to_delete"

        result = delete_session(
            session_id=session_id, session_service=mock_session_service
        )

        mock_session_service.delete_session.assert_called_once_with(session_id)
        self.assertEqual(
            result, {"message": f"Successfully deleted session {session_id}."}
        )

    def test_delete_session_failure(self):
        """
        Tests that the tool returns an error if the session_service raises an exception.
        """
        mock_session_service = MagicMock()
        session_id = "session_to_fail"
        error_message = "Test exception"
        mock_session_service.delete_session.side_effect = Exception(error_message)

        result = delete_session(
            session_id=session_id, session_service=mock_session_service
        )

        mock_session_service.delete_session.assert_called_once_with(session_id)
        self.assertIn("error", result)
        self.assertEqual(
            result["error"], f"Failed to delete session {session_id}: {error_message}"
        )


if __name__ == "__main__":
    unittest.main()
