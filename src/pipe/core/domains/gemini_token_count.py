"""
Domain logic for Gemini token counting.

This module provides pure functions for:
1. Counting tokens using Google's LocalTokenizer
2. Extracting token counts from API response statistics
3. Estimating tokens when tokenizer is unavailable
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.genai.local_tokenizer import LocalTokenizer


def create_local_tokenizer(model_name: str) -> LocalTokenizer | None:
    """Create a LocalTokenizer instance for the given model.

    Args:
        model_name: The model name to create a tokenizer for

    Returns:
        LocalTokenizer instance or None if unavailable
    """
    try:
        from google.genai.local_tokenizer import LocalTokenizer

        # Map unsupported model names to supported ones for tokenization
        # LocalTokenizer doesn't support all model names (e.g., gemini-3.x, preview models)
        # See: https://github.com/googleapis/python-genai/issues/1784
        # Workaround: Replace gemini-3.x with gemini-2.5-x and remove -preview suffix
        tokenizer_model_name = (
            model_name.replace("gemini-3.", "gemini-2.5-")
            .replace("gemini-3-", "gemini-2.5-")
            .replace("-preview", "")
        )
        return LocalTokenizer(model_name=tokenizer_model_name)
    except ImportError:
        # Silently fall back to estimation if dependencies are missing
        return None
    except Exception as e:
        print(f"Warning: Failed to initialize LocalTokenizer: {e}")
        print("Token counting will use fallback estimation.")
        return None


def count_tokens_with_tokenizer(
    tokenizer: LocalTokenizer,
    contents: str | dict | list,
    tools: list | None = None,
) -> int | None:
    """Count tokens using LocalTokenizer.

    Args:
        tokenizer: The LocalTokenizer instance to use
        contents: A string, dict, or list to count tokens for
        tools: Optional list of tool definitions to include in token count

    Returns:
        The total number of tokens, or None if tokenization fails
    """
    try:
        # Convert contents to string if needed
        if isinstance(contents, dict | list):
            text = json.dumps(contents, ensure_ascii=False)
        else:
            text = str(contents)

        # If tools are provided, append them to the text for counting
        if tools:
            tools_text = json.dumps(tools, ensure_ascii=False)
            text = text + "\n" + tools_text

        # Use LocalTokenizer to count tokens
        result = tokenizer.count_tokens(text)
        return result.total_tokens if result.total_tokens is not None else 0
    except Exception as e:
        print(f"Error counting tokens with LocalTokenizer: {e}")
        return None


def estimate_tokens(contents: str | dict | list, tools: list | None = None) -> int:
    """Rough token estimation based on characters (char_len / 4).

    Args:
        contents: A string, dict, or list to estimate tokens for
        tools: Optional list of tool definitions to include in estimation

    Returns:
        Estimated token count based on character length
    """
    total_chars = 0

    # Count characters from contents
    if isinstance(contents, str):
        total_chars += len(contents)
    elif isinstance(contents, dict):
        total_chars += len(json.dumps(contents, ensure_ascii=False))
    elif isinstance(contents, list):
        total_chars += sum(
            len(json.dumps(item, ensure_ascii=False)) for item in contents
        )

    # Count characters from tools
    if tools:
        total_chars += len(json.dumps(tools, ensure_ascii=False))

    return total_chars // 4


def count_tokens(
    contents: str | dict | list,
    tools: list | None = None,
    tokenizer: LocalTokenizer | None = None,
) -> int:
    """Count tokens using LocalTokenizer with fallback estimation.

    Args:
        contents: A string, dict, or list to count tokens for
        tools: Optional list of tool definitions to include in token count
        tokenizer: Optional LocalTokenizer instance. If None, uses estimation.

    Returns:
        The total number of tokens (accurate if tokenizer provided, estimated otherwise)
    """
    if tokenizer:
        token_count = count_tokens_with_tokenizer(tokenizer, contents, tools)
        if token_count is not None:
            return token_count
        # Fall through to estimation if tokenization failed

    # Fallback estimation when tokenizer is unavailable or fails
    print("GeminiTokenCount: Using rough fallback estimation.")
    return estimate_tokens(contents, tools)


def check_token_limit(tokens: int, limit: int) -> tuple[bool, str]:
    """Check if the token count is within the specified limit.

    Args:
        tokens: The number of tokens to check
        limit: The maximum allowed token count

    Returns:
        A tuple containing a boolean (True if within limit) and a status message
    """
    is_within_limit = tokens <= limit
    message = f"{tokens} / {limit} tokens"
    return is_within_limit, message
