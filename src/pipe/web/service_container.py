"""Service container for dependency injection.

This module provides a simple service container pattern to share
services across route blueprints without circular imports.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipe.core.models.settings import Settings
    from pipe.core.services.file_indexer_service import FileIndexerService
    from pipe.core.services.procedure_service import ProcedureService
    from pipe.core.services.role_service import RoleService
    from pipe.core.services.search_sessions_service import SearchSessionsService
    from pipe.core.services.session_artifact_service import SessionArtifactService
    from pipe.core.services.session_management_service import SessionManagementService
    from pipe.core.services.session_meta_service import SessionMetaService
    from pipe.core.services.session_optimization_service import (
        SessionOptimizationService,
    )
    from pipe.core.services.session_reference_service import SessionReferenceService
    from pipe.core.services.session_service import SessionService
    from pipe.core.services.session_todo_service import SessionTodoService
    from pipe.core.services.session_tree_service import SessionTreeService
    from pipe.core.services.session_turn_service import SessionTurnService
    from pipe.core.services.session_workflow_service import SessionWorkflowService
    from pipe.web.controllers import (
        SessionChatController,
        SessionManagementController,
        StartSessionController,
    )


class ServiceContainer:
    """Container for application services."""

    def __init__(self):
        self._session_service: SessionService | None = None
        self._session_management_service: SessionManagementService | None = None
        self._session_tree_service: SessionTreeService | None = None
        self._session_workflow_service: SessionWorkflowService | None = None
        self._session_optimization_service: SessionOptimizationService | None = None
        self._session_reference_service: SessionReferenceService | None = None
        self._session_artifact_service: SessionArtifactService | None = None
        self._session_turn_service: SessionTurnService | None = None
        self._session_meta_service: SessionMetaService | None = None
        self._session_todo_service: SessionTodoService | None = None
        self._start_session_controller: StartSessionController | None = None
        self._session_chat_controller: SessionChatController | None = None
        self._session_management_controller: SessionManagementController | None = None
        self._file_indexer_service: FileIndexerService | None = None
        self._search_sessions_service: SearchSessionsService | None = None
        self._procedure_service: ProcedureService | None = None
        self._role_service: RoleService | None = None
        self._settings: Settings | None = None
        self._project_root: str | None = None

    def init(
        self,
        session_service: "SessionService",
        session_management_service: "SessionManagementService",
        session_tree_service: "SessionTreeService",
        session_workflow_service: "SessionWorkflowService",
        session_optimization_service: "SessionOptimizationService",
        session_reference_service: "SessionReferenceService",
        session_artifact_service: "SessionArtifactService",
        session_turn_service: "SessionTurnService",
        session_meta_service: "SessionMetaService",
        session_todo_service: "SessionTodoService",
        start_session_controller: "StartSessionController",
        session_chat_controller: "SessionChatController",
        session_management_controller: "SessionManagementController",
        file_indexer_service: "FileIndexerService",
        search_sessions_service: "SearchSessionsService",
        procedure_service: "ProcedureService",
        role_service: "RoleService",
        settings: "Settings",
        project_root: str,
    ) -> None:
        """Initialize the container with services."""
        self._session_service = session_service
        self._session_management_service = session_management_service
        self._session_tree_service = session_tree_service
        self._session_workflow_service = session_workflow_service
        self._session_optimization_service = session_optimization_service
        self._session_reference_service = session_reference_service
        self._session_artifact_service = session_artifact_service
        self._session_turn_service = session_turn_service
        self._session_meta_service = session_meta_service
        self._session_todo_service = session_todo_service
        self._start_session_controller = start_session_controller
        self._session_chat_controller = session_chat_controller
        self._session_management_controller = session_management_controller
        self._file_indexer_service = file_indexer_service
        self._search_sessions_service = search_sessions_service
        self._procedure_service = procedure_service
        self._role_service = role_service
        self._settings = settings
        self._project_root = project_root

    @property
    def session_service(self) -> "SessionService":
        if self._session_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_service

    @property
    def session_management_service(self) -> "SessionManagementService":
        if self._session_management_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_management_service

    @property
    def session_tree_service(self) -> "SessionTreeService":
        if self._session_tree_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_tree_service

    @property
    def session_workflow_service(self) -> "SessionWorkflowService":
        if self._session_workflow_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_workflow_service

    @property
    def session_optimization_service(self) -> "SessionOptimizationService":
        if self._session_optimization_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_optimization_service

    @property
    def session_reference_service(self) -> "SessionReferenceService":
        if self._session_reference_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_reference_service

    @property
    def session_artifact_service(self) -> "SessionArtifactService":
        if self._session_artifact_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_artifact_service

    @property
    def session_turn_service(self) -> "SessionTurnService":
        if self._session_turn_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_turn_service

    @property
    def session_meta_service(self) -> "SessionMetaService":
        if self._session_meta_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_meta_service

    @property
    def session_todo_service(self) -> "SessionTodoService":
        if self._session_todo_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_todo_service

    @property
    def start_session_controller(self) -> "StartSessionController":
        if self._start_session_controller is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._start_session_controller

    @property
    def session_chat_controller(self) -> "SessionChatController":
        if self._session_chat_controller is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_chat_controller

    @property
    def session_management_controller(self) -> "SessionManagementController":
        if self._session_management_controller is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._session_management_controller

    @property
    def file_indexer_service(self) -> "FileIndexerService":
        if self._file_indexer_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._file_indexer_service

    @property
    def search_sessions_service(self) -> "SearchSessionsService":
        if self._search_sessions_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._search_sessions_service

    @property
    def settings(self) -> "Settings":
        if self._settings is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._settings

    @property
    def project_root(self) -> str:
        if self._project_root is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._project_root

    @property
    def procedure_service(self) -> "ProcedureService":
        if self._procedure_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._procedure_service

    @property
    def role_service(self) -> "RoleService":
        if self._role_service is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._role_service


# Global container instance
_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get the global service container."""
    return _container


def get_session_service() -> "SessionService":
    """Get the session service from the container."""
    return _container.session_service


def get_session_management_service() -> "SessionManagementService":
    """Get the session management service from the container."""
    return _container.session_management_service


def get_session_tree_service() -> "SessionTreeService":
    """Get the session tree service from the container."""
    return _container.session_tree_service


def get_session_workflow_service() -> "SessionWorkflowService":
    """Get the session workflow service from the container."""
    return _container.session_workflow_service


def get_session_optimization_service() -> "SessionOptimizationService":
    """Get the session optimization service from the container."""
    return _container.session_optimization_service


def get_session_reference_service() -> "SessionReferenceService":
    """Get the session reference service from the container."""
    return _container.session_reference_service


def get_session_artifact_service() -> "SessionArtifactService":
    """Get the session artifact service from the container."""
    return _container.session_artifact_service


def get_session_turn_service() -> "SessionTurnService":
    """Get the session turn service from the container."""
    return _container.session_turn_service


def get_session_meta_service() -> "SessionMetaService":
    """Get the session meta service from the container."""
    return _container.session_meta_service


def get_session_todo_service() -> "SessionTodoService":
    """Get the session todo service from the container."""
    return _container.session_todo_service


def get_start_session_controller() -> "StartSessionController":
    """Get the start session controller from the container."""
    return _container.start_session_controller


def get_session_chat_controller() -> "SessionChatController":
    """Get the session chat controller from the container."""
    return _container.session_chat_controller


def get_session_management_controller() -> "SessionManagementController":
    """Get the session management controller from the container."""
    return _container.session_management_controller


def get_file_indexer_service() -> "FileIndexerService":
    """Get the file indexer service from the container."""
    return _container.file_indexer_service


def get_search_sessions_service() -> "SearchSessionsService":
    """Get the search sessions service from the container."""
    return _container.search_sessions_service


def get_settings() -> "Settings":
    """Get the settings from the container."""
    return _container.settings


def get_project_root() -> str:
    """Get the project root from the container."""
    return _container.project_root


def get_procedure_service() -> "ProcedureService":
    """Get the procedure service from the container."""
    return _container.procedure_service


def get_role_service() -> "RoleService":
    """Get the role service from the container."""
    return _container.role_service
