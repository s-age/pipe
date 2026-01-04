from unittest.mock import MagicMock, patch

import httpx
from pipe.core.models.results.web_fetch_result import WebFetchResult
from pipe.core.models.tool_result import ToolResult
from pipe.core.tools.web_fetch import web_fetch


class TestWebFetch:
    """Tests for web_fetch tool."""

    def test_web_fetch_no_urls(self):
        """Test web_fetch when no URLs are present in the prompt."""
        prompt = "This is a prompt without any links."
        result = web_fetch(prompt)

        assert isinstance(result, ToolResult)
        assert result.error == "No URLs found in the prompt."
        assert result.data is None

    @patch("pipe.core.tools.web_fetch.httpx.Client")
    def test_web_fetch_single_url_success(self, mock_client_class):
        """Test successful fetch and parse of a single URL."""
        # Setup mock client and response
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><head><style>.css{}</style></head><body><h1>Hello</h1><script>alert(1)</script><p>World</p></body></html>"
        mock_client.get.return_value = mock_response

        prompt = "Fetch this: https://example.com"
        result = web_fetch(prompt)

        assert result.is_success
        assert isinstance(result.data, WebFetchResult)
        # Check if script and style are removed and text is cleaned
        assert "Hello" in result.data.message
        assert "World" in result.data.message
        assert "alert(1)" not in result.data.message
        assert ".css" not in result.data.message
        assert "Successfully fetched and parsed content" in result.data.message

    @patch("pipe.core.tools.web_fetch.httpx.Client")
    def test_web_fetch_multiple_urls_success(self, mock_client_class):
        """Test successful fetch of multiple URLs."""
        mock_client = mock_client_class.return_value.__enter__.return_value

        res1 = MagicMock()
        res1.text = "<html><body>Page 1</body></html>"
        res2 = MagicMock()
        res2.text = "<html><body>Page 2</body></html>"

        mock_client.get.side_effect = [res1, res2]

        prompt = "Check https://one.com and http://two.org"
        result = web_fetch(prompt)

        assert result.is_success
        assert "Page 1" in result.data.message
        assert "Page 2" in result.data.message
        assert mock_client.get.call_count == 2

    @patch("pipe.core.tools.web_fetch.httpx.Client")
    def test_web_fetch_http_error(self, mock_client_class):
        """Test handling of HTTP status errors (e.g., 404)."""
        mock_client = mock_client_class.return_value.__enter__.return_value

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"
        # raise_for_status should raise HTTPStatusError
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=mock_response
        )
        mock_client.get.return_value = mock_response

        prompt = "https://broken.link"
        result = web_fetch(prompt)

        assert (
            result.is_success
        )  # The tool returns success but the message contains error info
        assert "HTTP Error: 404 Not Found" in result.data.message

    @patch("pipe.core.tools.web_fetch.httpx.Client")
    def test_web_fetch_request_error(self, mock_client_class):
        """Test handling of request errors (e.g., DNS failure)."""
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.side_effect = httpx.RequestError(
            "Connection failed", request=MagicMock()
        )

        prompt = "https://nonexistent.domain"
        result = web_fetch(prompt)

        assert result.is_success
        assert (
            "An error occurred while requesting the URL: Connection failed"
            in result.data.message
        )

    @patch("pipe.core.tools.web_fetch.httpx.Client")
    def test_web_fetch_unexpected_exception(self, mock_client_class):
        """Test handling of unexpected exceptions."""
        mock_client = mock_client_class.return_value.__enter__.return_value
        mock_client.get.side_effect = Exception("Unexpected boom")

        prompt = "https://example.com"
        result = web_fetch(prompt)

        assert result.is_success
        assert "An unexpected error occurred: Unexpected boom" in result.data.message

    @patch("pipe.core.tools.web_fetch.httpx.Client")
    def test_web_fetch_mixed_results(self, mock_client_class):
        """Test mixed success and failure with multiple URLs."""
        mock_client = mock_client_class.return_value.__enter__.return_value

        res_ok = MagicMock()
        res_ok.text = "<html><body>Success</body></html>"

        mock_client.get.side_effect = [
            res_ok,
            httpx.RequestError("Failed", request=MagicMock()),
        ]

        prompt = "https://ok.com and https://fail.com"
        result = web_fetch(prompt)

        assert result.is_success
        assert "Success" in result.data.message
        assert "--- Error fetching {url} ---" in result.data.message
