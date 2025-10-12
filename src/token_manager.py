"""
Manages token counting using the official Google Generative AI library.
"""

import os
import google.generativeai as genai
from google.generativeai import types

class TokenManager:
    """Handles token counting using the google-genai library."""

    def __init__(self, settings: dict):
        """
        Initializes the TokenManager.

        Args:
            settings: The settings dictionary containing model configuration.
        """
        self.model_name = settings.get('token_manager', {}).get('model', "gemini-2.5-flash")
        self.limit = settings.get('token_manager', {}).get('limit', 1000000)

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
