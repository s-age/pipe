"""
Manages token counting using the official Google Generative AI library.
"""

import os
import google.genai as genai
from google.genai import types

from pipe.core.models.settings import Settings

class TokenManager:
    """Handles token counting using the google-genai library."""

    def __init__(self, settings: Settings):
        """
        Initializes the TokenManager.

        Args:
            settings: The Settings model instance.
        """
        self.model_name = settings.model
        self.limit = settings.context_limit
        try:
            self.client = genai.Client()
        except Exception as e:
            print(f"Error initializing genai.Client: {e}")
            self.client = None

    def count_tokens(self, contents, tools: list | None = None) -> int:
        """
        Counts the number of tokens in the prompt contents using the Gemini API.

        Args:
            contents: A string or a list of content dictionaries.
            tools: An optional list of tool definitions.

        Returns:
            The total number of tokens, or a fallback estimation if an error occurs.
        """
        if not self.client:
            print("TokenManager: Client not initialized, cannot count tokens.")
            return 0
        try:
            response = self.client.models.count_tokens(model=self.model_name, contents=contents)
            return response.total_tokens
        except Exception as e:
            print(f"Error counting tokens via API: {e}")
            # As a rough fallback, estimate based on characters.
            estimated_tokens = 0
            if isinstance(contents, str):
                estimated_tokens = len(contents) // 4
            elif isinstance(contents, list):
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
