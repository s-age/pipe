# This script utilizes the 'google-genai' library to interact with the Gemini API.
# It is important to note that 'google-genai' is the newer, recommended library,
# and should be used in place of the older 'google-generativeai' library to ensure
# access to the latest features and improvements.
# For reference, see: https://pypi.org/project/google-genai/

from typing import TYPE_CHECKING

from pipe.core.agents import register_agent
from pipe.core.agents.base import BaseAgent
from pipe.core.models.args import TaktArgs

if TYPE_CHECKING:
    from pipe.core.services.prompt_service import PromptService
    from pipe.core.services.session_service import SessionService


@register_agent("gemini-api")
class GeminiApiAgent(BaseAgent):
    """Agent for Gemini API streaming mode."""

    def run(
        self,
        args: TaktArgs,
        session_service: "SessionService",
        prompt_service: "PromptService",
    ) -> tuple[str, int | None, list]:
        """Execute the Gemini API agent.

        This wraps the streaming call and returns the final result
        after all streaming is complete.

        Args:
            args: Command line arguments
            session_service: Service for session management
            prompt_service: Service for prompt building

        Returns:
            Tuple of (response_text, token_count, turns_to_save)
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_api_delegate
        from pipe.core.services.session_turn_service import SessionTurnService

        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )
        stream_results = list(
            gemini_api_delegate.run_stream(
                args, session_service, prompt_service, session_turn_service
            )
        )
        # The last yielded item contains the final result
        _, model_response_text, token_count, turns_to_save = stream_results[-1]

        return model_response_text, token_count, turns_to_save

    def run_stream(
        self,
        args: TaktArgs,
        session_service: "SessionService",
        prompt_service: "PromptService",
    ):
        """Execute the Gemini API agent in streaming mode.

        This method yields intermediate results for WebUI streaming support.

        Args:
            args: Command line arguments
            session_service: Service for session management
            prompt_service: Service for prompt building

        Yields:
            Intermediate streaming results and final tuple
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_api_delegate
        from pipe.core.services.session_turn_service import SessionTurnService

        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )
        yield from gemini_api_delegate.run_stream(
            args, session_service, prompt_service, session_turn_service
        )
