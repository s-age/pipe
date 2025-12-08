import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.delegates import fork_delegate
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings


class TestForkDelegate(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        settings_data = {
            "model": "test-model",
            "search_model": "test-model",
            "context_limit": 10000,
            "api_mode": "gemini-api",
            "language": "en",
            "yolo": False,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)

    @patch('pipe.core.delegates.fork_delegate.ServiceFactory')
    def test_run_fork_success(self, mock_factory_class):
        """Tests fork_delegate calls workflow_service.fork_session."""
        args = TaktArgs(fork="session-to-fork", at_turn=3)

        # Setup mock
        mock_factory = MagicMock()
        mock_workflow_service = MagicMock()
        mock_factory.create_session_workflow_service.return_value = (
            mock_workflow_service
        )
        mock_factory_class.return_value = mock_factory

        fork_delegate.run(args, self.project_root, self.settings)

        # at_turn is 1-based, so fork_session receives index 2
        mock_workflow_service.fork_session.assert_called_once_with(
            "session-to-fork", 2
        )

    def test_run_fork_without_at_turn(self):
        """Tests that a ValueError is raised if --at-turn is missing."""
        args = TaktArgs(fork="session-to-fork", at_turn=None)

        with self.assertRaisesRegex(ValueError, "Error: --at-turn is required"):
            fork_delegate.run(args, self.project_root, self.settings)

    @patch('pipe.core.delegates.fork_delegate.ServiceFactory')
    def test_run_fork_handles_service_errors(self, mock_factory_class):
        """Tests that errors from the workflow_service are propagated."""
        mock_factory = MagicMock()
        mock_workflow_service = MagicMock()
        mock_workflow_service.fork_session.side_effect = FileNotFoundError(
            "Session not found"
        )
        mock_factory.create_session_workflow_service.return_value = (
            mock_workflow_service
        )
        mock_factory_class.return_value = mock_factory

        args = TaktArgs(fork="non-existent-session", at_turn=1)

        with self.assertRaisesRegex(ValueError, "Error: Session not found"):
            fork_delegate.run(args, self.project_root, self.settings)


if __name__ == "__main__":
    unittest.main()
