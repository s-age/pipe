import io
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.delegates import dry_run_delegate
from pipe.core.models.prompt import Prompt
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService


class TestDryRunDelegate(unittest.TestCase):
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_run_prints_prompt_json(self, mock_stdout):
        """
        Tests that the dry_run delegate correctly calls the prompt service
        and prints the resulting model's JSON output.
        """
        # 1. Setup Mocks
        mock_session_service = MagicMock(spec=SessionService)
        mock_prompt_service = MagicMock(spec=PromptService)

        # Mock the return value of build_prompt to be a mock Prompt model
        mock_prompt_model = MagicMock(spec=Prompt)
        mock_prompt_model.model_dump_json.return_value = '{"key": "value"}'
        mock_prompt_service.build_prompt.return_value = mock_prompt_model

        # 2. Run the delegate
        dry_run_delegate.run(mock_session_service, mock_prompt_service)

        # 3. Assertions
        mock_prompt_service.build_prompt.assert_called_once_with(mock_session_service)
        self.assertEqual(mock_stdout.getvalue().strip(), '{"key": "value"}')


if __name__ == "__main__":
    unittest.main()
