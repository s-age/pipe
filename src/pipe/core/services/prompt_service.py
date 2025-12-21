"""
Service responsible for constructing the prompt object from session data.
"""

import os
from typing import TYPE_CHECKING

from jinja2 import Environment
from pipe.core.domains.artifacts import build_artifacts_from_data
from pipe.core.factories.prompt_factory import PromptFactory
from pipe.core.models.prompt import Prompt
from pipe.core.repositories.resource_repository import ResourceRepository
from pipe.core.services.session_service import SessionService

if TYPE_CHECKING:
    pass


class PromptService:
    """Constructs a structured Prompt object for the LLM."""

    def __init__(
        self,
        project_root: str,
        jinja_env: Environment,
        resource_repository: ResourceRepository,
    ):
        self.project_root = project_root
        self.jinja_env = jinja_env
        self.resource_repository = resource_repository
        self.prompt_factory = PromptFactory(project_root, resource_repository)

    def build_prompt(self, session_service: SessionService) -> Prompt:
        """
        Builds and returns a validated Prompt object by delegating to PromptFactory.
        """
        current_session = session_service.current_session
        settings = session_service.settings

        if not current_session:
            raise ValueError("Cannot build prompt without a current session.")

        processed_artifacts = None
        if current_session.artifacts:
            # Read artifact contents in Service layer
            artifacts_with_contents = []
            for artifact_path in current_session.artifacts:
                full_path = os.path.abspath(
                    os.path.join(self.project_root, artifact_path)
                )
                contents = None
                if self.resource_repository.exists(
                    full_path, allowed_root=self.project_root
                ):
                    contents = self.resource_repository.read_text(
                        full_path, allowed_root=self.project_root
                    )
                artifacts_with_contents.append((artifact_path, contents))

            # Use pure domain function for transformation
            processed_artifacts = build_artifacts_from_data(artifacts_with_contents)

        return self.prompt_factory.create(
            session=current_session,
            settings=settings,
            artifacts=processed_artifacts,
            current_instruction=session_service.current_instruction,
        )
