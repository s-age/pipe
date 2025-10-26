import unittest
from unittest.mock import MagicMock, patch
import argparse
import tempfile
import shutil
import os

from pipe.core.dispatcher import dispatch
from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService
from pipe.core.models.settings import Settings

class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.project_root, "sessions"))
        
        settings_data = {
            "model": "test-model", "search_model": "test-model", "context_limit": 10000,
            "api_mode": "gemini-api", "language": "en", "yolo": False, "expert_mode": False, "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"}
            }
        }
        self.settings = Settings(**settings_data)
        self.session_service = SessionService(project_root=self.project_root, settings=self.settings)
        self.mock_parser = MagicMock(spec=argparse.ArgumentParser)

    def tearDown(self):
        shutil.rmtree(self.project_root)

    @patch('pipe.core.delegates.fork_delegate.run')
    def test_dispatch_routes_to_fork_delegate(self, mock_fork_run):
        """Tests that dispatch() correctly routes to the fork_delegate."""
        args = TaktArgs(fork="some-session-id", at_turn=1)
        dispatch(args, self.session_service, self.mock_parser)
        mock_fork_run.assert_called_once_with(args, self.session_service)

    @patch('pipe.core.dispatcher._dispatch_run')
    def test_dispatch_routes_to_run_for_instruction(self, mock_dispatch_run):
        """Tests that dispatch() correctly routes to the internal _dispatch_run for an instruction."""
        args = TaktArgs(instruction="Do something", purpose="p", background="b")
        dispatch(args, self.session_service, self.mock_parser)
        # prepare_session_for_takt is called inside dispatch, we can check its effects
        self.assertIsNotNone(self.session_service.current_session)
        mock_dispatch_run.assert_called_once_with(args, self.session_service)

    @patch('pipe.core.delegates.help_delegate.run')
    def test_dispatch_routes_to_help_delegate(self, mock_help_run):
        """Tests that dispatch() correctly routes to the help_delegate when no command is given."""
        args = TaktArgs()
        dispatch(args, self.session_service, self.mock_parser)
        mock_help_run.assert_called_once_with(self.mock_parser)

    @patch('pipe.core.delegates.dry_run_delegate.run')
    @patch('pipe.core.delegates.gemini_api_delegate.run')
    def test_dispatch_run_handles_dry_run(self, mock_gemini_run, mock_dry_run):
        """Tests that _dispatch_run correctly routes to the dry_run_delegate."""
        from pipe.core.dispatcher import _dispatch_run
        
        args = TaktArgs(instruction="Do something", dry_run=True, purpose="p", background="b")
        self.session_service.prepare_session_for_takt(args) # Prepare the service state
        
        _dispatch_run(args, self.session_service)
        
        mock_dry_run.assert_called_once()
        mock_gemini_run.assert_not_called()

if __name__ == '__main__':
    unittest.main()