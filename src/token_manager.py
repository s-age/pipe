"""
Manages token counting using the official Google Generative AI library.
"""

import os
import google.generativeai as genai
from google.generativeai import types

class TokenManager:
    """Handles token counting using the google-genai library."""

    DEFAULT_MODEL = "gemini-1.5-flash"
    DEFAULT_LIMIT = 1000000

    def __init__(self, model_name: str = DEFAULT_MODEL, limit: int = DEFAULT_LIMIT):
        """
        Initializes the TokenManager.

        Args:
            model_name: The name of the generative model to use for token counting.
            limit: The context window limit for the model.
        """
        self.model_name = model_name
        self.limit = limit

    def count_tokens(self, contents: list[types.ContentDict], tools: list | None = None) -> int:
        """
        Counts the number of tokens in the prompt contents using the Gemini API.

        Args:
            contents: A list of content dictionaries.
            tools: An optional list of tool definitions.

        Returns:
            The total number of tokens, or a fallback estimation if an error occurs.
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.count_tokens(contents=contents, tools=tools)
            return response.total_tokens
        except Exception as e:
            print(f"Error counting tokens via API: {e}")
            # As a rough fallback, estimate based on characters.
            estimated_tokens = sum(len(part.get('text', '')) for content in contents for part in content.get('parts', [])) // 4
            print(f"Using rough fallback estimation: {estimated_tokens} tokens.")
            return estimated_tokens

    def check_limit(self, tokens: int) -> tuple[bool, str]:
        """
        Checks if the token count is within the specified limit.

        Args:
            tokens: The number of tokens to check.

        Returns:
            A tuple containing a boolean (True if within limit) and a status message.
        """
        is_within_limit = tokens <= self.limit
        message = f"{tokens} / {self.limit} tokens"
        return is_within_limit, message
