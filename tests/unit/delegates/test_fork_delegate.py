import unittest
from unittest.mock import MagicMock

from pipe.core.delegates import fork_delegate
from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService


class TestForkDelegate(unittest.TestCase):
    def setUp(self):
        self.mock_session_service = MagicMock(spec=SessionService)

    def test_run_fork_success(self):
        """Tests that the fork_delegate correctly calls session_service.fork_session."""
        args = TaktArgs(fork="session-to-fork", at_turn=3)

        fork_delegate.run(args, self.mock_session_service)

        # at_turn is 1-based, so fork_session receives index 2
        self.mock_session_service.fork_session.assert_called_once_with(
            "session-to-fork", 2
        )

    def test_run_fork_without_at_turn(self):
        """Tests that a ValueError is raised if --at-turn is missing."""
        args = TaktArgs(fork="session-to-fork", at_turn=None)

        with self.assertRaisesRegex(ValueError, "Error: --at-turn is required"):
            fork_delegate.run(args, self.mock_session_service)

    def test_run_fork_handles_service_errors(self):
        """Tests that errors from the session_service are propagated."""
        self.mock_session_service.fork_session.side_effect = FileNotFoundError(
            "Session not found"
        )
        args = TaktArgs(fork="non-existent-session", at_turn=1)

        with self.assertRaisesRegex(ValueError, "Error: Session not found"):
            fork_delegate.run(args, self.mock_session_service)


if __name__ == "__main__":
    unittest.main()
