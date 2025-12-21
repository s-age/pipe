import unittest
from unittest.mock import MagicMock, patch

from helpers import create_test_settings
from pipe.core.services.token_service import TokenService


class TestTokenService(unittest.TestCase):
    def setUp(self):
        """Set up a dummy Settings object for the service."""
        self.settings = create_test_settings(context_limit=1000)

    @patch("google.genai.Client")
    def test_count_tokens_success(self, mock_genai_client):
        """
        Tests the happy path where the API call to count_tokens succeeds.
        """
        # Configure the mock client and its return value
        mock_client_instance = MagicMock()
        mock_client_instance.models.count_tokens.return_value = MagicMock(
            total_tokens=123
        )
        mock_genai_client.return_value = mock_client_instance

        token_service = TokenService(self.settings)
        token_count = token_service.count_tokens("This is a test prompt.")

        # Assert that the service returned the value from the mock
        self.assertEqual(token_count, 123)
        mock_client_instance.models.count_tokens.assert_called_once()

    @patch("google.genai.Client")
    def test_count_tokens_api_error_fallback(self, mock_genai_client):
        """
        Tests the fallback mechanism when the API call to count_tokens fails.
        """
        # Configure the mock client to raise an exception
        mock_client_instance = MagicMock()
        mock_client_instance.models.count_tokens.side_effect = Exception("API Error")
        mock_genai_client.return_value = mock_client_instance

        token_service = TokenService(self.settings)
        test_prompt = (
            "This is a test prompt with some considerable length to test the fallback."
        )
        token_count = token_service.count_tokens(test_prompt)

        # Assert that the service returned the fallback estimation
        expected_fallback = len(test_prompt) // 4
        self.assertEqual(token_count, expected_fallback)
        mock_client_instance.models.count_tokens.assert_called_once()

    def test_check_limit(self):
        """
        Tests the check_limit method for both within-limit and over-limit cases.
        """
        token_service = TokenService(self.settings)  # No API call, so no mock needed

        # Case 1: Within limit
        is_within, message = token_service.check_limit(500)
        self.assertTrue(is_within)
        self.assertEqual(message, "500 / 1000 tokens")

        # Case 2: Over limit
        is_within, message = token_service.check_limit(1500)
        self.assertFalse(is_within)
        self.assertEqual(message, "1500 / 1000 tokens")


if __name__ == "__main__":
    unittest.main()
