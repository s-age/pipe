import unittest
from unittest.mock import MagicMock, patch

from pipe.core.agents.search_agent import call_gemini_api_with_grounding
from pipe.core.models.settings import Settings


class TestSearchAgent(unittest.TestCase):
    def setUp(self):
        """Set up dummy settings for the tests."""
        settings_data = {
            "model": "gemini-test-model",
            "search_model": "gemini-search-model",
            "context_limit": 10000,
            "api_mode": "gemini-api",
            "language": "en",
            "yolo": False,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.1, "description": "t"},
                "top_p": {"value": 0.2, "description": "p"},
                "top_k": {"value": 10, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)
        self.instruction = "Test instruction"
        self.project_root = "/fake/project/root"

    @patch("pipe.core.agents.search_agent.genai.Client")
    def test_successful_call(self, MockClient):
        """Tests a successful call to the Gemini API with grounding."""
        # Mock the client and its response
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [MagicMock()]
        mock_response.candidates[0].content.parts[
            0
        ].text = "This is the mocked response."
        mock_client_instance.models.generate_content.return_value = mock_response
        MockClient.return_value = mock_client_instance

        # Call the function
        response = call_gemini_api_with_grounding(
            self.settings, self.instruction, self.project_root
        )

        # Assertions
        self.assertIsNotNone(response)
        self.assertEqual(
            response.candidates[0].content.parts[0].text, "This is the mocked response."
        )

        # Check that the API was called with the correct parameters
        mock_client_instance.models.generate_content.assert_called_once()
        _, kwargs = mock_client_instance.models.generate_content.call_args
        self.assertEqual(kwargs["model"], "gemini-search-model")
        self.assertEqual(kwargs["contents"][0]["role"], "user")
        self.assertIn("google_search", str(kwargs["config"].tools))

    def test_missing_search_model(self):
        """Tests that a ValueError is raised if search_model is not set."""
        self.settings.search_model = None
        with self.assertRaisesRegex(
            ValueError, "'search_model' not found in setting.yml"
        ):
            call_gemini_api_with_grounding(
                self.settings, self.instruction, self.project_root
            )

    @patch("pipe.core.agents.search_agent.genai.Client")
    def test_api_error(self, MockClient):
        """Tests that a RuntimeError is raised when the API call fails."""
        # Mock the client to raise an exception
        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.side_effect = Exception(
            "API Failure"
        )
        MockClient.return_value = mock_client_instance

        with self.assertRaisesRegex(
            RuntimeError, "Error during Gemini API execution: API Failure"
        ):
            call_gemini_api_with_grounding(
                self.settings, self.instruction, self.project_root
            )


if __name__ == "__main__":
    unittest.main()
