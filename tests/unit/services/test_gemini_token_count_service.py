import unittest
from unittest.mock import MagicMock, patch

from pipe.core.services.gemini_token_count_service import GeminiTokenCountService
from pipe.core.services.gemini_tool_service import GeminiToolService

from tests.factories.models import create_test_settings


class TestGeminiTokenCountService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.settings = create_test_settings(context_limit=1000)
        self.tool_service = GeminiToolService()
        self.project_root = "/test/project/root"

    def test_count_tokens_with_local_tokenizer_success(self):
        """Test token counting with LocalTokenizer when it succeeds."""
        # Configure the mock tokenizer
        mock_tokenizer = MagicMock()
        mock_result = MagicMock()
        mock_result.total_tokens = 150
        mock_tokenizer.count_tokens.return_value = mock_result

        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )
        service.tokenizer = mock_tokenizer

        # Test counting tokens from a string
        token_count = service.count_tokens("This is a test prompt.")

        self.assertEqual(token_count, 150)
        mock_tokenizer.count_tokens.assert_called_once()

    def test_count_tokens_with_tools(self):
        """Test token counting including tools."""
        # Configure the mock tokenizer
        mock_tokenizer = MagicMock()
        mock_result = MagicMock()
        mock_result.total_tokens = 250
        mock_tokenizer.count_tokens.return_value = mock_result

        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )
        service.tokenizer = mock_tokenizer

        # Test with tools
        tools = [
            {"name": "test_tool", "description": "A test tool"},
            {"name": "another_tool", "description": "Another test tool"},
        ]
        token_count = service.count_tokens("Test prompt", tools=tools)

        self.assertEqual(token_count, 250)
        # Verify tools were included in the count
        call_args = mock_tokenizer.count_tokens.call_args[0][0]
        self.assertIn("test_tool", call_args)
        self.assertIn("another_tool", call_args)

    def test_count_tokens_fallback_when_tokenizer_unavailable(self):
        """Test fallback to character-based estimation when LocalTokenizer is unavailable."""
        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )
        # Force tokenizer to None (simulating import failure)
        service.tokenizer = None

        test_prompt = "This is a test prompt with some length."
        token_count = service.count_tokens(test_prompt)

        # Expected fallback: len(prompt) // 4
        expected = len(test_prompt) // 4
        self.assertEqual(token_count, expected)

    def test_count_tokens_fallback_with_tools(self):
        """Test fallback estimation includes tools."""
        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )
        service.tokenizer = None

        test_prompt = "Test prompt"
        tools = [{"name": "tool1"}, {"name": "tool2"}]
        token_count = service.count_tokens(test_prompt, tools=tools)

        # Manually calculate expected value
        import json

        prompt_chars = len(test_prompt)
        tools_chars = len(json.dumps(tools, ensure_ascii=False))
        expected = (prompt_chars + tools_chars) // 4

        self.assertEqual(token_count, expected)

    def test_count_tokens_handles_dict_and_list(self):
        """Test that dict and list inputs are properly converted to JSON."""
        mock_tokenizer = MagicMock()
        mock_result = MagicMock()
        mock_result.total_tokens = 100
        mock_tokenizer.count_tokens.return_value = mock_result

        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )
        service.tokenizer = mock_tokenizer

        # Test with dict
        dict_content = {"key": "value", "number": 42}
        token_count = service.count_tokens(dict_content)
        self.assertEqual(token_count, 100)

        # Test with list
        list_content = ["item1", "item2", "item3"]
        token_count = service.count_tokens(list_content)
        self.assertEqual(token_count, 100)

    def test_count_tokens_from_prompt(self):
        """Test count_tokens_from_prompt renders prompt and counts tokens."""
        mock_tokenizer = MagicMock()
        mock_result = MagicMock()
        mock_result.total_tokens = 500
        mock_tokenizer.count_tokens.return_value = mock_result

        # Mock services
        mock_session_service = MagicMock()
        mock_session_service.settings.api_mode = "gemini-cli"
        mock_prompt_service = MagicMock()
        mock_template = MagicMock()
        mock_template.render.return_value = '{"test": "prompt"}'
        mock_prompt_service.jinja_env.get_template.return_value = mock_template
        mock_prompt_service.build_prompt.return_value = MagicMock()

        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )
        service.tokenizer = mock_tokenizer

        # Mock tool loading
        with patch.object(service.tool_service, "load_tools", return_value=[]):
            token_count = service.count_tokens_from_prompt(
                mock_session_service, mock_prompt_service
            )

        self.assertEqual(token_count, 500)
        mock_prompt_service.build_prompt.assert_called_once()
        mock_template.render.assert_called_once()

    def test_check_limit_within_limit(self):
        """Test check_limit when tokens are within the limit."""
        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )

        is_within, message = service.check_limit(500)

        self.assertTrue(is_within)
        self.assertEqual(message, "500 / 1000 tokens")

    def test_check_limit_exceeds_limit(self):
        """Test check_limit when tokens exceed the limit."""
        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )

        is_within, message = service.check_limit(1500)

        self.assertFalse(is_within)
        self.assertEqual(message, "1500 / 1000 tokens")

    def test_tokenizer_error_falls_back_to_estimation(self):
        """Test that tokenizer errors trigger fallback to estimation."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.count_tokens.side_effect = Exception("Tokenizer error")

        service = GeminiTokenCountService(
            settings=self.settings,
            tool_service=self.tool_service,
            project_root=self.project_root,
        )
        service.tokenizer = mock_tokenizer

        test_prompt = "This is a test prompt."
        token_count = service.count_tokens(test_prompt)

        # Should fall back to character-based estimation
        expected = len(test_prompt) // 4
        self.assertEqual(token_count, expected)


if __name__ == "__main__":
    unittest.main()
