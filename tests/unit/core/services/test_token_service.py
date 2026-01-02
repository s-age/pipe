"""
Unit tests for TokenService.
"""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.services.token_service import TokenService

from tests.factories.models import create_test_settings


@pytest.fixture
def mock_settings():
    """Create mock settings for TokenService."""
    return create_test_settings(
        model_name="gemini-1.5-flash",
        context_limit=100000,
    )


class TestTokenServiceInit:
    """Tests for TokenService.__init__."""

    @patch("google.genai.Client")
    def test_init_success(self, mock_genai_client, mock_settings):
        """Test successful initialization when google.genai is available."""
        service = TokenService(mock_settings)
        assert service.model_name == "gemini-1.5-flash"
        assert service.limit == 100000
        assert service.client is not None
        mock_genai_client.assert_called_once()

    def test_init_import_error(self, mock_settings):
        """Test initialization when google.genai is not available."""
        # Mock __import__ to raise ImportError for google.genai
        original_import = __import__

        def mocked_import(name, *args, **kwargs):
            if name == "google.genai":
                raise ImportError("Mocked import error")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mocked_import):
            with patch("pipe.core.services.token_service.print") as mock_print:
                service = TokenService(mock_settings)
                assert service.client is None
                mock_print.assert_any_call(
                    "TokenService: google.genai not available; "
                    "skipping client initialization."
                )

    @patch("google.genai.Client")
    def test_init_client_exception(self, mock_genai_client, mock_settings):
        """Test initialization when genai.Client() raises an exception."""
        mock_genai_client.side_effect = Exception("Connection error")

        with patch("pipe.core.services.token_service.print") as mock_print:
            service = TokenService(mock_settings)
            assert service.client is None
            mock_print.assert_any_call(
                "Error initializing genai.Client: Connection error"
            )


class TestTokenServiceCountTokens:
    """Tests for TokenService.count_tokens."""

    @patch("google.genai.Client")
    def test_count_tokens_api_success(self, mock_genai_client, mock_settings):
        """Test successful token counting via API."""
        service = TokenService(mock_settings)
        mock_response = MagicMock()
        mock_response.total_tokens = 123
        service.client.models.count_tokens.return_value = mock_response

        result = service.count_tokens("test content")

        assert result == 123
        service.client.models.count_tokens.assert_called_once_with(
            model="gemini-1.5-flash", contents="test content"
        )

    @patch("google.genai.Client")
    def test_count_tokens_api_returns_none(self, mock_genai_client, mock_settings):
        """Test API returning None for total_tokens."""
        service = TokenService(mock_settings)
        mock_response = MagicMock()
        mock_response.total_tokens = None
        service.client.models.count_tokens.return_value = mock_response

        result = service.count_tokens("test content")

        assert result == 0

    @patch("google.genai.Client")
    def test_count_tokens_api_exception_fallback(
        self, mock_genai_client, mock_settings
    ):
        """Test fallback to estimation when API raises an exception."""
        service = TokenService(mock_settings)
        service.client.models.count_tokens.side_effect = Exception("API Error")

        with patch.object(
            service, "_estimate_tokens_locally", return_value=42
        ) as mock_estimate:
            with patch("pipe.core.services.token_service.print") as mock_print:
                result = service.count_tokens("test content")
                assert result == 42
                mock_print.assert_any_call("Error counting tokens via API: API Error")
                mock_estimate.assert_called_once_with("test content")

    def test_count_tokens_no_client_fallback(self, mock_settings):
        """Test fallback to estimation when client is None."""
        with patch("google.genai.Client", side_effect=Exception):
            service = TokenService(mock_settings)

        assert service.client is None

        with patch.object(
            service, "_estimate_tokens_locally", return_value=10
        ) as mock_estimate:
            result = service.count_tokens("test content")
            assert result == 10
            mock_estimate.assert_called_once_with("test content")


class TestTokenServiceEstimateTokensLocally:
    """Tests for TokenService._estimate_tokens_locally."""

    def test_estimate_string(self, mock_settings):
        """Test estimation with string input."""
        service = TokenService(mock_settings)
        # "12345678" -> 8 chars -> 8 // 4 = 2
        assert service._estimate_tokens_locally("12345678") == 2
        # "123" -> 3 chars -> 3 // 4 = 0
        assert service._estimate_tokens_locally("123") == 0

    def test_estimate_list(self, mock_settings):
        """Test estimation with list of content dictionaries."""
        service = TokenService(mock_settings)
        contents = [
            {"parts": [{"text": "hello "}, {"text": "world"}]},  # 6 + 5 = 11
            {"parts": [{"text": "!!!"}]},  # 3
        ]
        # Total chars = 14. 14 // 4 = 3.
        assert service._estimate_tokens_locally(contents) == 3

    def test_estimate_list_empty_parts(self, mock_settings):
        """Test estimation with list containing empty parts."""
        service = TokenService(mock_settings)
        contents = [
            {"parts": []},
            {"parts": [{"not_text": "..."}]},
        ]
        assert service._estimate_tokens_locally(contents) == 0

    def test_estimate_invalid_input(self, mock_settings):
        """Test estimation with invalid input type."""
        service = TokenService(mock_settings)
        assert service._estimate_tokens_locally(123) == 0
        assert service._estimate_tokens_locally(None) == 0


class TestTokenServiceCheckLimit:
    """Tests for TokenService.check_limit."""

    def test_check_limit_within(self, mock_settings):
        """Test check_limit when within limit."""
        service = TokenService(mock_settings)
        service.limit = 100
        is_within, message = service.check_limit(50)
        assert is_within is True
        assert message == "50 / 100 tokens"

    def test_check_limit_exactly(self, mock_settings):
        """Test check_limit when exactly at limit."""
        service = TokenService(mock_settings)
        service.limit = 100
        is_within, message = service.check_limit(100)
        assert is_within is True
        assert message == "100 / 100 tokens"

    def test_check_limit_exceeded(self, mock_settings):
        """Test check_limit when exceeding limit."""
        service = TokenService(mock_settings)
        service.limit = 100
        is_within, message = service.check_limit(101)
        assert is_within is False
        assert message == "101 / 100 tokens"
