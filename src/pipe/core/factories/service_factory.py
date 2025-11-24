"""
Factory for creating and wiring up application services.
"""

import os

from jinja2 import Environment, FileSystemLoader
from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService


class ServiceFactory:
    """
    Handles the creation and dependency injection of services.
    """

    def __init__(self, project_root: str, settings: Settings):
        self.project_root = project_root
        self.settings = settings
        self.jinja_env = self._create_jinja_environment()

    def _create_jinja_environment(self) -> Environment:
        template_path = os.path.join(self.project_root, "templates", "prompt")
        loader = FileSystemLoader(template_path)
        return Environment(loader=loader, autoescape=False)

    def create_session_service(self) -> SessionService:
        """Creates a SessionService with its dependencies."""
        repository = SessionRepository(self.project_root, self.settings)
        service = SessionService(self.project_root, self.settings, repository)
        return service

    def create_prompt_service(self) -> PromptService:
        """Creates a PromptService with its dependencies."""
        return PromptService(self.project_root, self.jinja_env)

    def create_file_indexer_service(self) -> FileIndexerService:
        """Creates a FileIndexerService with its dependencies."""
        return FileIndexerService(self.project_root)
