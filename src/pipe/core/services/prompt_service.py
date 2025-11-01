"""
Service responsible for constructing the prompt object from session data.
"""

from jinja2 import Environment
from pipe.core.domains.artifacts import process_artifacts_for_session
from pipe.core.models.prompt import Prompt
from pipe.core.services.session_service import SessionService


class PromptService:
    """Constructs a structured Prompt object for the LLM."""

    def __init__(self, project_root: str, jinja_env: Environment):
        self.project_root = project_root
        self.jinja_env = jinja_env

    def build_prompt(self, session_service: SessionService) -> Prompt:
        """
        Builds and returns a validated Prompt object by delegating to the current
        session.
        """
        current_session = session_service.current_session
        settings = session_service.settings

        if not current_session:
            raise ValueError("Cannot build prompt without a current session.")

        processed_artifacts = (
            process_artifacts_for_session(current_session.artifacts, self.project_root)
            if current_session.artifacts
            else None
        )

        return Prompt.from_session(
            current_session, settings, self.project_root, artifacts=processed_artifacts
        )
