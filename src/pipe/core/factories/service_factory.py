"""
Factory for creating and wiring up application services.
"""

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pipe.core.models.settings import Settings
from pipe.core.repositories.procedure_repository import ProcedureRepository
from pipe.core.repositories.role_repository import RoleRepository
from pipe.core.repositories.session_repository import SessionRepository
from pipe.core.services.file_indexer_service import FileIndexerService
from pipe.core.services.procedure_service import ProcedureService
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.role_service import RoleService
from pipe.core.services.session_management_service import SessionManagementService
from pipe.core.services.session_meta_service import SessionMetaService
from pipe.core.services.session_optimization_service import SessionOptimizationService
from pipe.core.services.session_reference_service import SessionReferenceService
from pipe.core.services.session_service import SessionService
from pipe.core.services.session_todo_service import SessionTodoService
from pipe.core.services.session_tree_service import SessionTreeService
from pipe.core.services.session_turn_service import SessionTurnService
from pipe.core.services.session_workflow_service import SessionWorkflowService


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
        file_indexer = self.create_file_indexer_service()
        service = SessionService(
            self.project_root, self.settings, repository, file_indexer
        )
        return service

    def create_prompt_service(self) -> PromptService:
        """Creates a PromptService with its dependencies."""
        return PromptService(self.project_root, self.jinja_env)

    def create_file_indexer_service(self) -> FileIndexerService:
        """Creates a FileIndexerService with its dependencies."""
        return FileIndexerService(self.project_root)

    def create_session_management_service(self) -> SessionManagementService:
        """Creates a SessionManagementService with its dependencies."""
        repository = SessionRepository(self.project_root, self.settings)
        return SessionManagementService(repository)

    def create_procedure_service(self) -> ProcedureService:
        """Creates a ProcedureService with its dependencies."""
        procedures_root_dir = Path(self.project_root) / "procedures"
        repository = ProcedureRepository(procedures_root_dir)
        return ProcedureService(repository)

    def create_role_service(self) -> RoleService:
        """Creates a RoleService with its dependencies."""
        roles_root_dir = Path(self.project_root) / "roles"
        repository = RoleRepository(roles_root_dir)
        return RoleService(repository)

    def create_session_tree_service(self) -> SessionTreeService:
        """Creates a SessionTreeService with its dependencies."""
        session_service = self.create_session_service()
        return SessionTreeService(session_service)

    def create_session_workflow_service(self) -> SessionWorkflowService:
        """Creates a SessionWorkflowService with its dependencies."""
        session_service = self.create_session_service()
        return SessionWorkflowService(session_service)

    def create_session_optimization_service(self) -> SessionOptimizationService:
        """Creates a SessionOptimizationService with its dependencies."""
        session_service = self.create_session_service()
        return SessionOptimizationService(self.project_root, session_service)

    def create_session_reference_service(self) -> SessionReferenceService:
        """Creates a SessionReferenceService with its dependencies."""
        session_service = self.create_session_service()
        return SessionReferenceService(self.project_root, session_service)

    def create_session_turn_service(self) -> SessionTurnService:
        """Creates a SessionTurnService with its dependencies."""
        session_service = self.create_session_service()
        return SessionTurnService(self.settings, session_service)

    def create_session_meta_service(self) -> SessionMetaService:
        """Creates a SessionMetaService with its dependencies."""
        session_service = self.create_session_service()
        return SessionMetaService(session_service)

    def create_session_todo_service(self) -> SessionTodoService:
        """Creates a SessionTodoService with its dependencies."""
        session_service = self.create_session_service()
        return SessionTodoService(session_service)
