import unittest
from unittest.mock import MagicMock, patch

import httpx  # Import the library to use its specific exception
from pipe.core.tools.web_fetch import web_fetch


class TestWebFetchTool(unittest.TestCase):
    @patch("pipe.core.tools.web_fetch.httpx.Client")
    def test_web_fetch_success(self, mock_client):
        """
        Tests that web_fetch correctly extracts a URL, fetches content, and returns it.
        """
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><h1>Test Page</h1></body></html>"
        mock_response.raise_for_status.return_value = None

        # Setup mock client context manager
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value.get.return_value = mock_response
        mock_client.return_value = mock_context_manager

        prompt = "Please summarize the content of https://example.com/test"
        result = web_fetch(prompt)

        # Assertions
        self.assertIn("message", result)
        self.assertNotIn("error", result)
        self.assertIn("Successfully fetched and parsed content", result["message"])
        self.assertIn("Test Page", result["message"])
        mock_context_manager.__enter__.return_value.get.assert_called_once_with(
            "https://example.com/test", timeout=10.0
        )

    def test_web_fetch_no_url_in_prompt(self):
        """
        Tests that web_fetch returns an error if no URL is found in the prompt.
        """
        prompt = "Please summarize the content of the attached document."
        result = web_fetch(prompt)

        self.assertIn("error", result)
        self.assertEqual(result["error"], "No URLs found in the prompt.")

    @patch("pipe.core.tools.web_fetch.httpx.Client")
    def test_web_fetch_http_error(self, mock_client):
        """
        Tests that web_fetch handles HTTP status errors gracefully using the actual
        httpx exception.
        """
        # Setup a mock request object needed by HTTPStatusError
        mock_request = MagicMock(spec=httpx.Request)
        mock_request.method = "GET"
        mock_request.url = "http://example.com/notfound"

        # Setup mock response for an error
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"

        # Create the specific exception instance
        http_error = httpx.HTTPStatusError(
            "404 Not Found", request=mock_request, response=mock_response
        )

        # Make the mock's get call raise this specific exception
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value.get.side_effect = http_error
        mock_client.return_value = mock_context_manager

        prompt = "Get data from http://example.com/notfound"
        result = web_fetch(prompt)

        self.assertIn("message", result)
        self.assertIn(
            "--- Error fetching http://example.com/notfound ---", result["message"]
        )
        self.assertIn("HTTP Error: 404 Not Found", result["message"])


if __name__ == "__main__":
    unittest.main()
