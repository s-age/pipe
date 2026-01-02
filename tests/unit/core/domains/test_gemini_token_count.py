"""Unit tests for Gemini token counting domain logic."""

import json
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.domains.gemini_token_count import (
    check_token_limit,
    count_tokens,
    count_tokens_with_tokenizer,
    create_local_tokenizer,
    estimate_tokens,
)


class TestCreateLocalTokenizer:
    """Tests for create_local_tokenizer function."""

    @patch("google.genai.local_tokenizer.LocalTokenizer")
    def test_create_local_tokenizer_success(self, mock_local_tokenizer):
        """Test successful creation of LocalTokenizer."""
        mock_instance = MagicMock()
        mock_local_tokenizer.return_value = mock_instance

        result = create_local_tokenizer("gemini-1.5-flash")

        assert result == mock_instance
        mock_local_tokenizer.assert_called_once_with(model_name="gemini-1.5-flash")

    @patch("google.genai.local_tokenizer.LocalTokenizer")
    def test_create_local_tokenizer_mapping(self, mock_local_tokenizer):
        """Test model name mapping for LocalTokenizer."""
        create_local_tokenizer("gemini-3.0")
        mock_local_tokenizer.assert_called_with(model_name="gemini-2.5-0")

        create_local_tokenizer("gemini-3-flash")
        mock_local_tokenizer.assert_called_with(model_name="gemini-2.5-flash")

        create_local_tokenizer("gemini-1.5-pro-preview")
        mock_local_tokenizer.assert_called_with(model_name="gemini-1.5-pro")

    @patch("google.genai.local_tokenizer.LocalTokenizer")
    def test_create_local_tokenizer_import_error(self, mock_local_tokenizer):
        """Test handling of ImportError."""
        mock_local_tokenizer.side_effect = ImportError
        result = create_local_tokenizer("gemini-1.5-flash")
        assert result is None

    @patch("google.genai.local_tokenizer.LocalTokenizer")
    def test_create_local_tokenizer_exception(self, mock_local_tokenizer):
        """Test handling of general Exception."""
        mock_local_tokenizer.side_effect = Exception("Test error")
        result = create_local_tokenizer("gemini-1.5-flash")
        assert result is None


class TestCountTokensWithTokenizer:
    """Tests for count_tokens_with_tokenizer function."""

    @pytest.fixture
    def mock_tokenizer(self):
        """Fixture for a mock LocalTokenizer."""
        tokenizer = MagicMock()
        result = MagicMock()
        result.total_tokens = 10
        tokenizer.count_tokens.return_value = result
        return tokenizer

    def test_count_tokens_string(self, mock_tokenizer):
        """Test counting tokens for a string."""
        result = count_tokens_with_tokenizer(mock_tokenizer, "hello world")
        assert result == 10
        mock_tokenizer.count_tokens.assert_called_once_with("hello world")

    def test_count_tokens_dict(self, mock_tokenizer):
        """Test counting tokens for a dict."""
        contents = {"key": "value"}
        result = count_tokens_with_tokenizer(mock_tokenizer, contents)
        assert result == 10
        expected_text = json.dumps(contents, ensure_ascii=False)
        mock_tokenizer.count_tokens.assert_called_once_with(expected_text)

    def test_count_tokens_list(self, mock_tokenizer):
        """Test counting tokens for a list."""
        contents = ["item1", "item2"]
        result = count_tokens_with_tokenizer(mock_tokenizer, contents)
        assert result == 10
        expected_text = json.dumps(contents, ensure_ascii=False)
        mock_tokenizer.count_tokens.assert_called_once_with(expected_text)

    def test_count_tokens_with_tools(self, mock_tokenizer):
        """Test counting tokens with tools."""
        contents = "hello"
        tools = [{"name": "tool1"}]
        result = count_tokens_with_tokenizer(mock_tokenizer, contents, tools=tools)
        assert result == 10
        expected_text = "hello\n" + json.dumps(tools, ensure_ascii=False)
        mock_tokenizer.count_tokens.assert_called_once_with(expected_text)

    def test_count_tokens_exception(self, mock_tokenizer):
        """Test handling of exception during token counting."""
        mock_tokenizer.count_tokens.side_effect = Exception("Test error")
        result = count_tokens_with_tokenizer(mock_tokenizer, "hello")
        assert result is None

    def test_count_tokens_none_result(self, mock_tokenizer):
        """Test handling of None total_tokens in result."""
        mock_tokenizer.count_tokens.return_value.total_tokens = None
        result = count_tokens_with_tokenizer(mock_tokenizer, "hello")
        assert result == 0


class TestEstimateTokens:
    """Tests for estimate_tokens function."""

    def test_estimate_tokens_string(self):
        """Test estimation for a string."""
        # 12 chars / 4 = 3
        assert estimate_tokens("123456789012") == 3

    def test_estimate_tokens_dict(self):
        """Test estimation for a dict."""
        contents = {"a": 1}  # '{"a": 1}' is 8 chars
        assert estimate_tokens(contents) == 2

    def test_estimate_tokens_list(self):
        """Test estimation for a list."""
        contents = ["a", "b"]  # '"a"' is 3 chars, '"b"' is 3 chars. Total 6.
        # Wait, estimate_tokens implementation:
        # total_chars += sum(len(json.dumps(item, ensure_ascii=False)) for item in contents)
        # json.dumps("a") -> '"a"' (3 chars)
        # json.dumps("b") -> '"b"' (3 chars)
        # total = 6. 6 // 4 = 1.
        assert estimate_tokens(contents) == 1

    def test_estimate_tokens_with_tools(self):
        """Test estimation with tools."""
        contents = "1234"  # 4 chars
        tools = [{"n": "t"}]  # '[{"n": "t"}]' is 12 chars
        # total = 16. 16 // 4 = 4.
        assert estimate_tokens(contents, tools=tools) == 4


class TestCountTokens:
    """Tests for count_tokens function."""

    @patch("pipe.core.domains.gemini_token_count.count_tokens_with_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.estimate_tokens")
    def test_count_tokens_with_tokenizer_success(
        self, mock_estimate, mock_count_with_tok
    ):
        """Test count_tokens when tokenizer succeeds."""
        mock_tokenizer = MagicMock()
        mock_count_with_tok.return_value = 50

        result = count_tokens("content", tokenizer=mock_tokenizer)

        assert result == 50
        mock_count_with_tok.assert_called_once_with(mock_tokenizer, "content", None)
        mock_estimate.assert_not_called()

    @patch("pipe.core.domains.gemini_token_count.count_tokens_with_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.estimate_tokens")
    def test_count_tokens_with_tokenizer_failure(
        self, mock_estimate, mock_count_with_tok
    ):
        """Test count_tokens when tokenizer fails (returns None)."""
        mock_tokenizer = MagicMock()
        mock_count_with_tok.return_value = None
        mock_estimate.return_value = 20

        result = count_tokens("content", tokenizer=mock_tokenizer)

        assert result == 20
        mock_count_with_tok.assert_called_once()
        mock_estimate.assert_called_once_with("content", None)

    @patch("pipe.core.domains.gemini_token_count.estimate_tokens")
    def test_count_tokens_without_tokenizer(self, mock_estimate):
        """Test count_tokens when no tokenizer is provided."""
        mock_estimate.return_value = 30

        result = count_tokens("content")

        assert result == 30
        mock_estimate.assert_called_once_with("content", None)


class TestCheckTokenLimit:
    """Tests for check_token_limit function."""

    def test_check_token_limit_within(self):
        """Test when tokens are within limit."""
        is_within, message = check_token_limit(80, 100)
        assert is_within is True
        assert message == "80 / 100 tokens"

    def test_check_token_limit_at(self):
        """Test when tokens are exactly at limit."""
        is_within, message = check_token_limit(100, 100)
        assert is_within is True
        assert message == "100 / 100 tokens"

    def test_check_token_limit_over(self):
        """Test when tokens are over limit."""
        is_within, message = check_token_limit(120, 100)
        assert is_within is False
        assert message == "120 / 100 tokens"
