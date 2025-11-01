import io
import json
import unittest
from unittest.mock import MagicMock, patch

from jinja2 import Environment
from pipe.core.delegates import dry_run_delegate
from pipe.core.models.prompt import Prompt
from pipe.core.models.settings import Settings
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService


class TestDryRunDelegate(unittest.TestCase):
    def setUp(self):
        self.project_root = "/tmp/test_project"
        self.settings = Settings(
            model="test-model",
            search_model="test-model",
            context_limit=10000,
            api_mode="gemini-api",
            language="en",
            yolo=False,
            expert_mode=False,
            timezone="UTC",
            parameters={
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        )
        # Create a dummy Jinja2 environment for testing
        self.mock_jinja_env = MagicMock(spec=Environment)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_run_prints_prompt_json(self, mock_stdout):
        """
        Tests that the dry_run delegate correctly calls the prompt service
        and prints the resulting model's JSON output.
        """
        # 1. Setup Mocks
        mock_session_service = MagicMock(spec=SessionService)
        mock_session_service.settings = self.settings
        mock_prompt_service = MagicMock(spec=PromptService)
        mock_prompt_service.jinja_env = self.mock_jinja_env

        # Mock the return value of build_prompt to be a mock Prompt model
        mock_prompt_model = MagicMock(spec=Prompt)
        mock_prompt_model.model_dump_json.return_value = '{"key": "value"}'
        mock_prompt_service.build_prompt.return_value = mock_prompt_model

        # Mock the render method of the template
        mock_template = MagicMock()
        mock_template.render.return_value = '{"key": "value"}'
        mock_prompt_service.jinja_env.get_template.return_value = mock_template

        # 2. Run the delegate
        dry_run_delegate.run(mock_session_service, mock_prompt_service)

        # 3. Assertions
        mock_prompt_service.build_prompt.assert_called_once_with(mock_session_service)
        mock_prompt_service.jinja_env.get_template.assert_called_once_with(
            "gemini_api_prompt.j2"
        )
        mock_template.render.assert_called_once_with(session=mock_prompt_model)
        self.assertEqual(json.loads(mock_stdout.getvalue().strip()), {"key": "value"})


if __name__ == "__main__":
    unittest.main()
