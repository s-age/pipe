"""
Service responsible for constructing the prompt object from session data.
"""

from pipe.core.models.prompt import Prompt
from pipe.core.services.session_service import SessionService


class PromptService:
    """Constructs a structured Prompt object for the LLM."""

    def __init__(self, project_root: str):
        self.project_root = project_root

    def build_prompt(self, session_service: SessionService) -> Prompt:
        """
        Builds and returns a validated Prompt object by delegating to the current
        session.
        """
        current_session = session_service.current_session
        settings = session_service.settings

        if not current_session:
            raise ValueError("Cannot build prompt without a current session.")

        return current_session.to_prompt(settings, self.project_root)
