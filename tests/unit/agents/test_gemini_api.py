import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pipe.core.agents.gemini_api import call_gemini_api, load_tools


class TestLoadTools(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory for each test."""
        self.project_root = tempfile.mkdtemp()
        self.tools_dir = os.path.join(self.project_root, "src", "pipe", "core", "tools")
        os.makedirs(self.tools_dir)

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.project_root)

    def test_load_tools_various_params(self):
        """Tests loading tools with a variety of parameter types."""
        # Create a comprehensive set of mock tools
        with open(os.path.join(self.tools_dir, "tool_simple.py"), "w") as f:
            f.write(
                '''
def tool_simple(param1: str, param2: int):
    """A simple tool."""
    pass
'''
            )
        with open(os.path.join(self.tools_dir, "tool_complex.py"), "w") as f:
            f.write(
                '''
from typing import List, Optional, Union

def tool_complex(
    required_param: str,
    optional_param: Union[str, None] = None,
    list_param: Optional[List[str]] = None,
):
    """A complex tool."""
    pass
'''
            )
        with open(os.path.join(self.tools_dir, "tool_dicts.py"), "w") as f:
            f.write(
                '''
from typing import Dict, List

def tool_dicts(dict_param: Dict, list_dict_param: List[Dict]):
    """A tool with dicts."""
    pass
'''
            )
        with open(os.path.join(self.tools_dir, "tool_injected.py"), "w") as f:
            f.write(
                '''
def tool_injected(session_service: str, project_root: str, real_param: bool):
    """A tool with injected params."""
    pass
'''
            )
        with open(os.path.join(self.tools_dir, "tool_mismatch.py"), "w") as f:
            f.write(
                '''
def some_other_name():
    """Function name != file name."""
    pass
'''
            )

        tool_defs = load_tools(self.project_root)
        self.assertEqual(len(tool_defs), 4)  # tool_mismatch should be ignored

        # Sort for predictable order
        tool_defs.sort(key=lambda x: x["name"])

        # Assertions for tool_complex
        complex_tool = tool_defs[0]
        self.assertEqual(complex_tool["name"], "tool_complex")
        self.assertEqual(complex_tool["parameters"]["required"], ["required_param"])

        # Assertions for tool_dicts
        dict_tool = tool_defs[1]
        self.assertEqual(dict_tool["name"], "tool_dicts")
        self.assertEqual(
            dict_tool["parameters"]["properties"]["dict_param"]["type"], "object"
        )
        self.assertEqual(
            dict_tool["parameters"]["properties"]["list_dict_param"]["items"]["type"],
            "object",
        )

        # Assertions for tool_injected
        injected_tool = tool_defs[2]
        self.assertEqual(injected_tool["name"], "tool_injected")
        self.assertEqual(
            injected_tool["parameters"]["properties"].keys(), {"real_param"}
        )
        self.assertEqual(injected_tool["parameters"]["required"], ["real_param"])

        # Assertions for tool_simple
        simple_tool = tool_defs[3]
        self.assertEqual(simple_tool["name"], "tool_simple")
        self.assertEqual(simple_tool["parameters"]["required"], ["param1", "param2"])

    def test_load_tools_no_dir(self):
        """Tests load_tools with a non-existent tools directory."""
        shutil.rmtree(self.tools_dir)
        tool_defs = load_tools(self.project_root)
        self.assertEqual(tool_defs, [])

    def test_load_tools_invalid_syntax(self):
        """Tests that a tool with invalid syntax is gracefully skipped."""
        with open(os.path.join(self.tools_dir, "tool_invalid.py"), "w") as f:
            f.write("def tool_invalid(param1: str ->)")  # Invalid syntax

        with open(os.path.join(self.tools_dir, "tool_valid.py"), "w") as f:
            f.write(
                """
def tool_valid():
    pass
"""
            )

        tool_defs = load_tools(self.project_root)
        self.assertEqual(len(tool_defs), 1)
        self.assertEqual(tool_defs[0]["name"], "tool_valid")


@patch("pipe.core.agents.gemini_api.Environment")
@patch("pipe.core.agents.gemini_api.TokenService")
@patch("pipe.core.agents.gemini_api.load_tools")
@patch("pipe.core.agents.gemini_api.genai.Client")
class TestCallGeminiApi(unittest.TestCase):
    def setUp(self):
        self.mock_session_service = MagicMock()
        self.mock_prompt_service = MagicMock()

        # Configure mock session service
        self.mock_session_service.settings.parameters.temperature.value = 0.5
        self.mock_session_service.settings.parameters.top_p.value = 0.5
        self.mock_session_service.settings.parameters.top_k.value = 20
        self.mock_session_service.current_session.session_id = "test_session_123"
        self.mock_session_service.current_session.hyperparameters = None
        self.mock_session_service.project_root = "/fake/root"

        # Configure mock prompt service
        self.mock_prompt_service.build_prompt.return_value.model_dump.return_value = {}
        self.mock_prompt_service.project_root = "/fake/root"

    def test_successful_call(
        self, MockClient, mock_load_tools, MockTokenService, MockEnvironment
    ):
        """Tests a successful call to the streaming Gemini API."""
        # Configure mocks
        mock_env_instance = MockEnvironment.return_value
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered_prompt"
        mock_env_instance.get_template.return_value = mock_template
        MockTokenService.return_value.check_limit.return_value = (True, "OK")
        mock_load_tools.return_value = []
        mock_client_instance = MockClient.return_value
        mock_stream = [MagicMock()]
        mock_client_instance.models.generate_content_stream.return_value = mock_stream

        # Call the function
        generator = call_gemini_api(self.mock_session_service, self.mock_prompt_service)
        result = list(generator)

        # Assertions
        self.assertEqual(result, mock_stream)
        mock_client_instance.models.generate_content_stream.assert_called_once()
        self.assertEqual(os.environ["PIPE_SESSION_ID"], "test_session_123")

    def test_token_limit_exceeded(
        self, MockClient, mock_load_tools, MockTokenService, MockEnvironment
    ):
        """Tests that a ValueError is raised if the token limit is exceeded."""
        mock_env_instance = MockEnvironment.return_value
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered_prompt"
        mock_env_instance.get_template.return_value = mock_template
        MockTokenService.return_value.check_limit.return_value = (
            False,
            "Token limit exceeded",
        )

        with self.assertRaisesRegex(ValueError, "Prompt exceeds context window limit"):
            list(call_gemini_api(self.mock_session_service, self.mock_prompt_service))

    def test_api_execution_error(
        self, MockClient, mock_load_tools, MockTokenService, MockEnvironment
    ):
        """Tests that a RuntimeError is raised on API execution failure."""
        mock_env_instance = MockEnvironment.return_value
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered_prompt"
        mock_env_instance.get_template.return_value = mock_template
        MockTokenService.return_value.check_limit.return_value = (True, "OK")
        mock_client_instance = MockClient.return_value
        mock_client_instance.models.generate_content_stream.side_effect = Exception(
            "API Error"
        )

        with self.assertRaisesRegex(RuntimeError, "Error during Gemini API execution"):
            list(call_gemini_api(self.mock_session_service, self.mock_prompt_service))

    def test_with_session_hyperparameters_and_tools(
        self, MockClient, mock_load_tools, MockTokenService, MockEnvironment
    ):
        """Tests that session hyperparameters and tools are correctly processed."""
        # Configure mocks
        mock_env_instance = MockEnvironment.return_value
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered_prompt"
        mock_env_instance.get_template.return_value = mock_template
        MockTokenService.return_value.check_limit.return_value = (True, "OK")

        # Mock session hyperparameters
        mock_hyperparams = MagicMock()
        mock_hyperparams.temperature.value = 0.99
        mock_hyperparams.top_p = None  # Test that None values are skipped
        mock_hyperparams.top_k.value = 50
        self.mock_session_service.current_session.hyperparameters = mock_hyperparams

        # Mock load_tools to return a tool definition
        mock_tool_def = {
            "name": "my_tool",
            "description": "A test tool",
            "parameters": {
                "type": "OBJECT",
                "properties": {"param": {"type": "string"}},
                "required": ["param"],
            },
        }
        mock_load_tools.return_value = [mock_tool_def]

        mock_client_instance = MockClient.return_value
        mock_client_instance.models.generate_content_stream.return_value = []

        # Call the function
        list(call_gemini_api(self.mock_session_service, self.mock_prompt_service))

        # Assertions
        mock_client_instance.models.generate_content_stream.assert_called_once()
        _, kwargs = mock_client_instance.models.generate_content_stream.call_args
        config = kwargs["config"]

        # Check that session hyperparameters were used
        self.assertEqual(config.temperature, 0.99)
        self.assertEqual(config.top_p, 0.5)  # Should fall back to default
        self.assertEqual(config.top_k, 50)

        # Check that tools were converted and included
        self.assertEqual(len(config.tools), 1)
        self.assertEqual(config.tools[0].function_declarations[0].name, "my_tool")


if __name__ == "__main__":
    unittest.main()
