"""
Manages token counting using the official Google Generative AI library.
"""

import os
import google.generativeai as genai
from google.generativeai.types import content_types

# Configure the API key from environment variables.
# It's configured here to ensure it's set before any model interactions.
try:
    # Attempt to configure the API key.
    # This is wrapped in a try-except block to prevent crashes if the
    # environment variable is not set, allowing the application to run
    # in modes that do not require API calls (e.g., viewing history).
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY environment variable not set. API calls will fail.")
    else:
        genai.configure(api_key=api_key)
except Exception as e:
    print(f"Warning: Failed to configure Google API key: {e}")

class TokenManager:
    """Handles token counting using the google.generativeai library."""

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
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            print(f"Error initializing GenerativeModel: {e}")
            self.model = None

    def count_tokens(self, contents: list[content_types.ContentDict]) -> int:
        """
        Counts the number of tokens in the prompt contents using the Gemini API.

        Args:
            contents: A list of content dictionaries, matching the format
                      expected by the google-generativeai library
                      (e.g., [{"role": "user", "parts": [{"text": "..."}]}]).

        Returns:
            The total number of tokens, or 0 if an error occurs.
        """
        if not self.model:
            print("TokenManager: Model not initialized, cannot count tokens.")
            return 0
        try:
            response = self.model.count_tokens(contents)
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