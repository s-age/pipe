"""
Service for counting tokens using Google's LocalTokenizer.

This service uses the local tokenizer to count tokens without making API calls,
providing accurate token counts for Gemini models based on the rendered prompt.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from pipe.core.models.settings import Settings
from pipe.core.services.gemini_tool_service import GeminiToolService

if TYPE_CHECKING:
    from google.genai.local_tokenizer import LocalTokenizer
    from pipe.core.services.prompt_service import PromptService
    from pipe.core.services.session_service import SessionService


class GeminiTokenCountService:
    """Handles token counting using LocalTokenizer.

    This service counts tokens locally without API calls by:
    1. Rendering the prompt using the same logic as dry-run
    2. Loading tools using GeminiToolService
    3. Using LocalTokenizer to count tokens in the rendered prompt + tools
    4. Providing accurate token counts for context limit checks
    """

    def __init__(
        self,
        settings: Settings,
        tool_service: GeminiToolService,
        project_root: str,
    ):
        """Initialize the GeminiTokenCountService.

        Args:
            settings: The Settings model instance
            tool_service: The GeminiToolService instance for loading tools
            project_root: The project root directory path
        """
        self.model_name = settings.model.name
        self.limit = settings.model.context_limit
        self.tool_service = tool_service
        self.project_root = project_root
        self.tokenizer: LocalTokenizer | None = None

        # Import LocalTokenizer lazily
        try:
            from google.genai.local_tokenizer import LocalTokenizer

            # Map unsupported model names to supported ones for tokenization
            # LocalTokenizer doesn't support all model names (e.g., gemini-3.x, preview models)
            # See: https://github.com/googleapis/python-genai/issues/1784
            # Workaround: Replace gemini-3.x with gemini-2.5-x and remove -preview suffix
            tokenizer_model_name = (
                self.model_name.replace("gemini-3.", "gemini-2.5-")
                .replace("gemini-3-", "gemini-2.5-")
                .replace("-preview", "")
            )
            self.tokenizer = LocalTokenizer(model_name=tokenizer_model_name)
        except ImportError:
            # Silently fall back to estimation if dependencies are missing
            self.tokenizer = None
        except Exception as e:
            print(f"Warning: Failed to initialize LocalTokenizer: {e}")
            print("Token counting will use fallback estimation.")
            self.tokenizer = None

    def count_tokens_from_prompt(
        self,
        session_service: SessionService,
        prompt_service: PromptService,
    ) -> int:
        """Count tokens by rendering the prompt (dry-run style).

        This method:
        1. Builds the prompt model using PromptService
        2. Renders it to JSON (same as dry-run)
        3. Loads tools using GeminiToolService
        4. Counts tokens using LocalTokenizer (prompt + tools)

        Args:
            session_service: Session service for accessing session data
            prompt_service: Prompt service for building prompts

        Returns:
            Total number of tokens in the rendered prompt + tools
        """
        # Build prompt model (same as dry_run_delegate.py)
        prompt_model = prompt_service.build_prompt(session_service)

        # Determine which template to use based on api_mode
        template_name = (
            "gemini_api_prompt.j2"
            if session_service.settings.api_mode == "gemini-api"
            else "gemini_cli_prompt.j2"
        )
        template = prompt_service.jinja_env.get_template(template_name)

        # Render the template with the prompt model data
        rendered_prompt = template.render(session=prompt_model)

        # Load tools
        tools = self.tool_service.load_tools(self.project_root)

        # Count tokens using LocalTokenizer (includes tools)
        return self.count_tokens(rendered_prompt, tools=tools)

    def count_tokens(
        self, contents: str | dict | list, tools: list | None = None
    ) -> int:
        """Count tokens using LocalTokenizer, with fallback estimation.

        Args:
            contents: A string, dict, or list to count tokens for
            tools: Optional list of tool definitions to include in token count

        Returns:
            The total number of tokens, or a fallback estimation if tokenizer fails
        """
        if self.tokenizer:
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
                result = self.tokenizer.count_tokens(text)
                return result.total_tokens if result.total_tokens is not None else 0
            except Exception as e:
                print(f"Error counting tokens with LocalTokenizer: {e}")
                # Fall through to fallback estimation

        # Fallback estimation when tokenizer is unavailable or fails
        print("GeminiTokenCountService: Using rough fallback estimation.")
        return self._estimate_tokens_locally(contents, tools)

    def _estimate_tokens_locally(
        self, contents: str | dict | list, tools: list | None = None
    ) -> int:
        """Rough estimation based on characters (char_len / 4).

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

    def check_limit(self, tokens: int) -> tuple[bool, str]:
        """Check if the token count is within the specified limit.

        Args:
            tokens: The number of tokens to check

        Returns:
            A tuple containing a boolean (True if within limit) and a status message
        """
        is_within_limit = tokens <= self.limit
        message = f"{tokens} / {self.limit} tokens"
        return is_within_limit, message
