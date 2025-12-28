"""
Base payload builder for LLM agents.

Provides common functionality for loading session data and building prompts
without requiring PromptService. Each agent-specific payload builder should
inherit from this class and implement its own render logic.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pipe.core.models.prompt import Prompt

if TYPE_CHECKING:
    from pipe.core.services.session_service import SessionService


class BasePayloadBuilder(ABC):
    """
    Base class for building LLM payloads from session data.

    This class handles common session data loading and prompt object creation.
    Subclasses should implement the render() method to generate agent-specific
    payloads (JSON strings, API parameters, etc.).
    """

    def __init__(self, project_root: str):
        """
        Initialize the payload builder.

        Args:
            project_root: The project root directory
        """
        self.project_root = project_root

    def build_prompt_model(self, session_service: "SessionService") -> Prompt:
        """
        Build a Prompt object from session data.

        This method replicates the core functionality of PromptService.build_prompt()
        without requiring PromptService dependency.

        Args:
            session_service: Service containing session data

        Returns:
            A fully constructed Prompt object
        """
        import os

        from pipe.core.domains.artifacts import build_artifacts_from_data
        from pipe.core.factories.prompt_factory import PromptFactory
        from pipe.core.repositories.resource_repository import ResourceRepository

        current_session = session_service.current_session
        settings = session_service.settings

        if not current_session:
            raise ValueError("Cannot build prompt without a current session.")

        # Initialize repositories and factories
        resource_repository = ResourceRepository(self.project_root)
        prompt_factory = PromptFactory(self.project_root, resource_repository)

        # Process artifacts (read file contents)
        processed_artifacts = None
        if current_session.artifacts:
            artifacts_with_contents = []
            for artifact_path in current_session.artifacts:
                full_path = os.path.abspath(
                    os.path.join(self.project_root, artifact_path)
                )
                contents = None
                if resource_repository.exists(
                    full_path, allowed_root=self.project_root
                ):
                    contents = resource_repository.read_text(
                        full_path, allowed_root=self.project_root
                    )
                artifacts_with_contents.append((artifact_path, contents))

            processed_artifacts = build_artifacts_from_data(artifacts_with_contents)

        # Create and return the Prompt object
        return prompt_factory.create(
            session=current_session,
            settings=settings,
            artifacts=processed_artifacts,
            current_instruction=session_service.current_instruction,
        )

    @abstractmethod
    def render(self, prompt_model: Prompt) -> str:
        """
        Render the prompt model into an agent-specific payload format.

        This method must be implemented by subclasses to generate the
        appropriate payload format (JSON, text, etc.) for their specific
        LLM agent or API.

        Args:
            prompt_model: The Prompt object to render

        Returns:
            Rendered payload as a string
        """
        pass

    def build(self, session_service: "SessionService") -> str:
        """
        Build and render the complete payload.

        This is the main entry point that combines prompt model creation
        and rendering.

        Args:
            session_service: Service containing session data

        Returns:
            Rendered payload ready to send to the LLM
        """
        prompt_model = self.build_prompt_model(session_service)
        return self.render(prompt_model)
