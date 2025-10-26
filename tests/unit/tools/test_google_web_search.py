import unittest
from unittest.mock import patch, MagicMock

from pipe.core.tools.google_web_search import google_web_search
from pipe.core.models.settings import Settings

class TestGoogleWebSearchTool(unittest.TestCase):

    def setUp(self):
        settings_data = {
            "model": "test-model", "search_model": "test-search-model", "context_limit": 10000,
            "api_mode": "gemini-api", "language": "en", "yolo": False, "expert_mode": False, "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"}
            }
        }
        self.settings = Settings(**settings_data)
        self.project_root = "/fake/project/root"

    @patch('pipe.core.tools.google_web_search.call_gemini_api_with_grounding')
    def test_google_web_search_calls_api_and_returns_text(self, mock_call_api):
        """
        Tests that the google_web_search tool calls the grounding API
        and returns the text from the response.
        """
        # 1. Setup: Mock the API to return a response with text
        mock_response = MagicMock()
        mock_part = MagicMock()
        mock_part.text = "This is the search result."
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_part]
        mock_call_api.return_value = mock_response

        query = "What is the capital of France?"
        
        # 2. Run the tool
        result = google_web_search(
            query=query,
            settings=self.settings,
            project_root=self.project_root
        )

        # 3. Assertions
        mock_call_api.assert_called_once_with(
            settings=self.settings,
            instruction=query,
            project_root=self.project_root
        )
        
        self.assertIn("content", result)
        self.assertEqual(result["content"], "This is the search result.")

    @patch('pipe.core.tools.google_web_search.call_gemini_api_with_grounding')
    def test_google_web_search_handles_api_error(self, mock_call_api):
        """
        Tests that the tool handles exceptions from the API call gracefully.
        """
        # 1. Setup: Mock the API to raise an exception
        mock_call_api.side_effect = RuntimeError("API Failure")

        # 2. Run the tool
        result = google_web_search(
            query="test query",
            settings=self.settings,
            project_root=self.project_root
        )

        # 3. Assertions
        self.assertIn("error", result)
        self.assertIn("API Failure", result["error"])

if __name__ == '__main__':
    unittest.main()
