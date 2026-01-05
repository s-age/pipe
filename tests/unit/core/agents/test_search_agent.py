"""Unit tests for search_agent.py."""

import runpy
from unittest.mock import MagicMock, patch

import pytest
from google.genai import types
from pipe.core.agents.search_agent import call_gemini_api_with_grounding
from pipe.core.models.settings import Settings


class TestCallGeminiApiWithGrounding:
    """Tests for call_gemini_api_with_grounding function."""

    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        """Create a mock Settings object."""
        settings = MagicMock(spec=Settings)
        settings.search_model = MagicMock()
        settings.search_model.name = "gemini-2.0-flash-exp"
        settings.parameters = MagicMock()
        settings.parameters.temperature.value = 0.7
        settings.parameters.top_p.value = 0.9
        settings.parameters.top_k.value = 40
        return settings

    @patch("pipe.core.agents.search_agent.genai.Client")
    @patch("pipe.core.agents.search_agent.types.Tool")
    @patch("pipe.core.agents.search_agent.types.GoogleSearch")
    @patch("pipe.core.agents.search_agent.types.GenerateContentConfig")
    def test_call_gemini_api_with_grounding_success(
        self,
        mock_config_cls: MagicMock,
        mock_google_search_cls: MagicMock,
        mock_tool_cls: MagicMock,
        mock_client_cls: MagicMock,
        mock_settings: MagicMock,
    ) -> None:
        """Test successful Gemini API call with grounding."""
        # Setup mocks
        mock_client = mock_client_cls.return_value
        mock_response = MagicMock(spec=types.GenerateContentResponse)
        mock_client.models.generate_content.return_value = mock_response

        mock_google_search = mock_google_search_cls.return_value
        mock_tool = mock_tool_cls.return_value
        mock_config = mock_config_cls.return_value

        # Execute
        result = call_gemini_api_with_grounding(
            settings=mock_settings,
            instruction="What is the weather in Tokyo?",
            project_root="/mock/root",
        )

        # Assertions
        assert result == mock_response

        # Verify Tool creation
        mock_google_search_cls.assert_called_once()
        mock_tool_cls.assert_called_once_with(google_search=mock_google_search)

        # Verify Config creation
        mock_config_cls.assert_called_once_with(
            tools=[mock_tool], temperature=0.7, top_p=0.9, top_k=40
        )

        # Verify Client call
        mock_client.models.generate_content.assert_called_once_with(
            contents=[
                {"role": "user", "parts": [{"text": "What is the weather in Tokyo?"}]}
            ],
            config=mock_config,
            model="gemini-2.0-flash-exp",
        )

    def test_call_gemini_api_with_grounding_missing_search_model(
        self, mock_settings: MagicMock
    ) -> None:
        """Test ValueError when search_model is missing."""
        mock_settings.search_model = None

        with pytest.raises(ValueError, match="'search_model' not found in setting.yml"):
            call_gemini_api_with_grounding(mock_settings, "query", "/root")

    def test_call_gemini_api_with_grounding_missing_search_model_name(
        self, mock_settings: MagicMock
    ) -> None:
        """Test ValueError when search_model name is missing."""
        mock_settings.search_model.name = None

        with pytest.raises(ValueError, match="'search_model' not found in setting.yml"):
            call_gemini_api_with_grounding(mock_settings, "query", "/root")

    @patch("pipe.core.agents.search_agent.genai.Client")
    def test_call_gemini_api_with_grounding_api_error(
        self, mock_client_cls: MagicMock, mock_settings: MagicMock
    ) -> None:
        """Test RuntimeError when API call fails."""
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.side_effect = Exception("API failure")

        with pytest.raises(
            RuntimeError, match="Error during Gemini API execution: API failure"
        ):
            call_gemini_api_with_grounding(mock_settings, "query", "/root")


class TestMainBlock:
    """Tests for the if __name__ == "__main__": block."""

    @patch("sys.exit")
    @patch("builtins.print")
    def test_main_no_args(self, mock_print: MagicMock, mock_exit: MagicMock) -> None:
        """Test main block with no arguments."""
        mock_exit.side_effect = SystemExit(1)
        with patch("sys.argv", ["search_agent.py"]):
            with pytest.raises(SystemExit):
                runpy.run_path(
                    "src/pipe/core/agents/search_agent.py", run_name="__main__"
                )
        mock_print.assert_called_with("Usage: python search_agent.py <query>")
        mock_exit.assert_called_with(1)

    @patch("pipe.core.agents.search_agent.get_project_root")
    @patch("pipe.core.agents.search_agent.read_yaml_file")
    @patch("pipe.core.agents.search_agent.Settings")
    @patch("google.genai.Client")
    @patch("builtins.print")
    def test_main_success(
        self,
        mock_print: MagicMock,
        mock_client_cls: MagicMock,
        mock_settings_cls: MagicMock,
        mock_read_yaml: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test main block successful execution."""
        mock_get_root.return_value = "/mock/root"
        mock_read_yaml.return_value = {"some": "settings"}

        mock_settings = MagicMock()
        mock_settings.search_model.name = "gemini-2.0-flash-exp"
        mock_settings.parameters.temperature.value = 0.7
        mock_settings.parameters.top_p.value = 0.9
        mock_settings.parameters.top_k.value = 40
        mock_settings_cls.return_value = mock_settings

        mock_client = mock_client_cls.return_value
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "Search result"
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        with patch("sys.argv", ["search_agent.py", "my query"]):
            runpy.run_path("src/pipe/core/agents/search_agent.py", run_name="__main__")

            mock_print.assert_any_call("Search result")

    @patch("pipe.core.agents.search_agent.get_project_root")
    @patch("pipe.core.agents.search_agent.read_yaml_file")
    @patch("pipe.core.agents.search_agent.Settings")
    @patch("google.genai.Client")
    @patch("builtins.print")
    def test_main_no_response(
        self,
        mock_print: MagicMock,
        mock_client_cls: MagicMock,
        mock_settings_cls: MagicMock,
        mock_read_yaml: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test main block with no response from model."""
        mock_get_root.return_value = "/mock/root"
        mock_read_yaml.return_value = {}

        mock_settings = MagicMock()
        mock_settings.search_model.name = "gemini-2.0-flash-exp"
        mock_settings.parameters.temperature.value = 0.7
        mock_settings.parameters.top_p.value = 0.9
        mock_settings.parameters.top_k.value = 40
        mock_settings_cls.return_value = mock_settings

        mock_client = mock_client_cls.return_value
        mock_response = MagicMock()
        mock_response.candidates = []
        mock_client.models.generate_content.return_value = mock_response

        with patch("sys.argv", ["search_agent.py", "query"]):
            runpy.run_path("src/pipe/core/agents/search_agent.py", run_name="__main__")
            mock_print.assert_called_with("No response from model.")

    @patch("pipe.core.agents.search_agent.get_project_root")
    @patch("pipe.core.agents.search_agent.read_yaml_file")
    @patch("pipe.core.agents.search_agent.Settings")
    @patch("google.genai.Client")
    @patch("builtins.print")
    def test_main_error(
        self,
        mock_print: MagicMock,
        mock_client_cls: MagicMock,
        mock_settings_cls: MagicMock,
        mock_read_yaml: MagicMock,
        mock_get_root: MagicMock,
    ) -> None:
        """Test main block with execution error."""
        mock_get_root.return_value = "/mock/root"
        mock_read_yaml.return_value = {}

        mock_settings = MagicMock()
        mock_settings.search_model.name = "gemini-2.0-flash-exp"
        mock_settings.parameters.temperature.value = 0.7
        mock_settings.parameters.top_p.value = 0.9
        mock_settings.parameters.top_k.value = 40
        mock_settings_cls.return_value = mock_settings

        mock_client = mock_client_cls.return_value
        mock_client.models.generate_content.side_effect = Exception("Test Error")

        with patch("sys.argv", ["search_agent.py", "query"]):
            runpy.run_path("src/pipe/core/agents/search_agent.py", run_name="__main__")
            mock_print.assert_called_with(
                "Error: Error during Gemini API execution: Test Error"
            )
