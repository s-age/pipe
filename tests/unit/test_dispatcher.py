import argparse
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

from pipe.core.dispatcher import dispatch
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_service import SessionService


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.project_root, "sessions"))

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
        self.mock_repository = Mock(spec=SessionRepository)
        self.session_service = SessionService(
            project_root=self.project_root,
            settings=self.settings,
            repository=self.mock_repository,
        )
        self.mock_parser = MagicMock(spec=argparse.ArgumentParser)

    def tearDown(self):
        shutil.rmtree(self.project_root)

    @patch("pipe.core.delegates.fork_delegate.run")
    def test_dispatch_routes_to_fork_delegate(self, mock_fork_run):
        """Tests that dispatch() correctly routes to the fork_delegate."""
        args = TaktArgs(fork="some-session-id", at_turn=1)
        dispatch(args, self.session_service, self.mock_parser)
        mock_fork_run.assert_called_once_with(args, self.session_service)

    @patch("pipe.core.dispatcher._dispatch_run")
    def test_dispatch_routes_to_run_for_instruction(self, mock_dispatch_run):
        """Tests that dispatch() correctly routes to the internal _dispatch_run for
        an instruction."""
        args = TaktArgs(instruction="Do something", purpose="p", background="b")
        dispatch(args, self.session_service, self.mock_parser)
        self.assertIsNotNone(self.session_service.current_session)
        mock_dispatch_run.assert_called_once_with(args, self.session_service)

    @patch("pipe.core.delegates.help_delegate.run")
    def test_dispatch_routes_to_help_delegate(self, mock_help_run):
        """Tests that dispatch() correctly routes to the help_delegate when no
        command is given."""
        args = TaktArgs()
        dispatch(args, self.session_service, self.mock_parser)
        mock_help_run.assert_called_once_with(self.mock_parser)

    @patch(
        "pipe.core.delegates.gemini_api_delegate.run_stream",
        return_value=[("end", "model response", 100, [])],
    )
    @patch("pipe.core.delegates.dry_run_delegate.run")
    def test_dispatch_run_handles_dry_run(self, mock_dry_run, mock_gemini_run):
        """Tests that _dispatch_run correctly routes to the dry_run_delegate."""
        from pipe.core.dispatcher import _dispatch_run

        args = TaktArgs(
            instruction="Do something", dry_run=True, purpose="p", background="b"
        )
        self.session_service.prepare(args, is_dry_run=True)
        _dispatch_run(args, self.session_service)
        mock_dry_run.assert_called_once()
        mock_gemini_run.assert_not_called()

    @patch(
        "pipe.core.agents.gemini_api.GeminiApiAgent.run",
        return_value=("model response", 100, []),
    )
    def test_dispatch_run_handles_gemini_api_mode(self, mock_agent_run):
        """Tests that _dispatch_run routes to gemini_api_delegate via registry."""
        from pipe.core.dispatcher import _dispatch_run

        self.session_service.settings.api_mode = "gemini-api"
        args = TaktArgs(instruction="Do something", purpose="p", background="b")
        # Create a mock session with a mock references collection
        mock_session = MagicMock()
        from pipe.core.collections.references import ReferenceCollection

        mock_session.references = MagicMock(spec=ReferenceCollection, return_value=[])
        self.mock_repository.find.return_value = mock_session
        self.session_service.prepare(args, is_dry_run=False)
        _dispatch_run(args, self.session_service)
        mock_agent_run.assert_called_once()

    @patch(
        "pipe.core.agents.gemini_cli.GeminiCliAgent.run",
        return_value=("cli response", 100, []),
    )
    def test_dispatch_run_handles_gemini_cli_mode(self, mock_agent_run):
        """Tests that _dispatch_run routes to gemini_cli_delegate via registry."""
        from pipe.core.dispatcher import _dispatch_run

        self.session_service.settings.api_mode = "gemini-cli"
        args = TaktArgs(instruction="Do something", purpose="p", background="b")
        # Create a mock session with a mock references collection
        mock_session = MagicMock()
        from pipe.core.collections.references import ReferenceCollection

        mock_session.references = MagicMock(spec=ReferenceCollection, return_value=[])
        self.mock_repository.find.return_value = mock_session
        self.session_service.prepare(args, is_dry_run=False)
        _dispatch_run(args, self.session_service)
        mock_agent_run.assert_called_once()

    def test_dispatch_run_handles_unknown_api_mode(self):
        """Tests that _dispatch_run raises ValueError for an unknown api_mode."""
        from pipe.core.dispatcher import _dispatch_run

        self.session_service.settings.api_mode = "unknown-api"
        args = TaktArgs(instruction="Do something", purpose="p", background="b")
        # Create a mock session with a mock references collection
        mock_session = MagicMock()
        from pipe.core.collections.references import ReferenceCollection

        mock_session.references = MagicMock(spec=ReferenceCollection, return_value=[])
        self.mock_repository.find.return_value = mock_session
        self.session_service.prepare(args, is_dry_run=False)
        # The registry pattern now raises ValueError with a more descriptive message
        with self.assertRaisesRegex(ValueError, r"Unknown api_mode.*Available agents"):
            _dispatch_run(args, self.session_service)

    @patch(
        "pipe.core.agents.gemini_api.GeminiApiAgent.run",
        return_value=("model response", 100, []),
    )
    def test_ttl_and_expiration_are_called(self, mock_agent_run):
        """Tests that TTL decrement and tool response expiration are called."""
        from pipe.core.dispatcher import _dispatch_run

        args = TaktArgs(instruction="Do something", purpose="p", background="b")
        mock_session_service = MagicMock(spec=SessionService)
        mock_session_service.settings = self.settings
        mock_session_service.current_session_id = "test_session"
        mock_session_service.project_root = self.project_root  # Set attribute
        _dispatch_run(args, mock_session_service)
        mock_session_service.decrement_all_references_ttl_in_session.assert_called_once()
        mock_session_service.expire_old_tool_responses.assert_called_once()
        mock_agent_run.assert_called_once()

    @patch("pipe.core.delegates.dry_run_delegate.run")
    def test_dry_run_does_not_call_ttl_or_expiration(self, mock_dry_run):
        """Tests that TTL and expiration methods are NOT called on a dry run."""
        from pipe.core.dispatcher import _dispatch_run

        args = TaktArgs(
            instruction="Do something", dry_run=True, purpose="p", background="b"
        )
        mock_session_service = MagicMock(spec=SessionService)
        mock_session_service.settings = self.settings
        mock_session_service.current_session_id = "test_session"
        mock_session_service.project_root = self.project_root  # Set attribute
        _dispatch_run(args, mock_session_service)
        mock_session_service.decrement_all_references_ttl_in_session.assert_not_called()
        mock_session_service.expire_old_tool_responses.assert_not_called()
        mock_dry_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
