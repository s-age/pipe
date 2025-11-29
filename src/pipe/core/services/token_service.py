"""
Manages token counting using the official Google Generative AI library.
This module is defensive: if the `google.genai` package isn't available
in the runtime environment, TokenService will fall back to a noop client
and provide rough token estimations.
"""

from typing import Any

from pipe.core.models.settings import Settings


class TokenService:
    """Handles token counting using the google-genai library.

    If the `google.genai` package is not installed, the service will keep
    `self.client` as None and use a fallback estimation in `count_tokens()`.
    """

    def __init__(self, settings: Settings):
        """Initializes the TokenService.

        Args:
            settings: The Settings model instance.
        """
        self.model_name = settings.model
        self.limit = settings.context_limit

        self.client: Any | None = None

        # Import `google.genai` lazily so importing this module doesn't
        # raise ModuleNotFoundError in environments where the package
        # isn't installed (e.g., some Docker images).
        try:
            import google.genai as genai  # type: ignore

            try:
                self.client = genai.Client()
            except Exception as e:
                print(f"Error initializing genai.Client: {e}")
                self.client = None
        except Exception:
            # The google-genai package isn't available; proceed without it.
            print(
                "TokenService: google.genai not available; "
                "skipping client initialization."
            )
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
            print("TokenService: Client not initialized, cannot count tokens.")
            return 0
        try:
            response = self.client.models.count_tokens(
                model=self.model_name, contents=contents
            )
            return response.total_tokens if response.total_tokens is not None else 0
        except Exception as e:
            print(f"Error counting tokens via API: {e}")
            # As a rough fallback, estimate based on characters.
            estimated_tokens = 0
            if isinstance(contents, str):
                estimated_tokens = len(contents) // 4
            elif isinstance(contents, list):
                estimated_tokens = (
                    sum(
                        len(part.get("text", ""))
                        for content in contents
                        for part in content.get("parts", [])
                    )
                    // 4
                )
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
