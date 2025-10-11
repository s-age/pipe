"""
Manages token counting using the official Google Generative AI library.
"""

import os
from google import genai
from google.genai import types

# The genai.Client will automatically pick up the API key from environment variables
# (GOOGLE_API_KEY or GEMINI_API_KEY).

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
        try:
            self.client = genai.Client()
        except Exception as e:
            print(f"Error initializing genai.Client: {e}")
            self.client = None

    def count_tokens(self, contents: list[types.ContentDict]) -> int:
        """
        Counts the number of tokens in the prompt contents using the Gemini API.

        Args:
            contents: A list of content dictionaries, matching the format
                      expected by the google-genai library
                      (e.g., [{"role": "user", "parts": [{"text": "..."}]}]).

        Returns:
            The total number of tokens, or 0 if an error occurs.
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
            # This is not accurate but better than nothing if the API call fails.
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