"""
Factory for creating and wiring up application services.
"""

from pipe.core.models.settings import Settings
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.session_service import SessionService


class ServiceFactory:
    """
    Handles the creation and dependency injection of services.
    """

    def __init__(self, project_root: str, settings: Settings):
        self.project_root = project_root
        self.settings = settings

    def create_session_service(self) -> SessionService:
        """Creates a SessionService with its dependencies."""
        repository = SessionRepository(self.project_root, self.settings)
        service = SessionService(self.project_root, self.settings, repository)
        return service
