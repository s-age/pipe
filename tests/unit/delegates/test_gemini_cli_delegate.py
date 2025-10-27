import unittest
import zoneinfo
from unittest.mock import MagicMock, patch

from pipe.core.delegates import gemini_cli_delegate
from pipe.core.models.args import TaktArgs
from pipe.core.services.session_service import SessionService


class TestGeminiCliDelegate(unittest.TestCase):
    @patch("pipe.core.delegates.gemini_cli_delegate.call_gemini_cli")
    def test_run_passes_correct_arguments(self, mock_call_gemini_cli):
        """
        Tests that the gemini_cli delegate correctly calls the underlying
        call_gemini_cli function with the right arguments.
        """
        # 1. Setup Mocks
        mock_session_service = MagicMock(spec=SessionService)
        mock_session_service.current_session_id = "test_session"
        mock_session_service.timezone_obj = zoneinfo.ZoneInfo("UTC")
        mock_call_gemini_cli.return_value = "Mocked response"
        args = TaktArgs(instruction="Test instruction")

        # 2. Run the delegate
        gemini_cli_delegate.run(args, mock_session_service)

        # 3. Assertions
        mock_call_gemini_cli.assert_called_once_with(mock_session_service)


if __name__ == "__main__":
    unittest.main()
