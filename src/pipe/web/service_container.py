"""Service container for dependency injection.

This module provides a simple service container pattern to share
services across route blueprints without circular imports.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pipe.core.models.settings import Settings
    from pipe.core.services.file_indexer_service import FileIndexerService
    from pipe.core.services.session_management_service import SessionManagementService
    from pipe.core.services.session_service import SessionService
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
        self._start_session_controller: StartSessionController | None = None
        self._session_chat_controller: SessionChatController | None = None
        self._session_management_controller: SessionManagementController | None = None
        self._file_indexer_service: FileIndexerService | None = None
        self._settings: Settings | None = None
        self._project_root: str | None = None

    def init(
        self,
        session_service: "SessionService",
        session_management_service: "SessionManagementService",
        start_session_controller: "StartSessionController",
        session_chat_controller: "SessionChatController",
        session_management_controller: "SessionManagementController",
        file_indexer_service: "FileIndexerService",
        settings: "Settings",
        project_root: str,
    ) -> None:
        """Initialize the container with services."""
        self._session_service = session_service
        self._session_management_service = session_management_service
        self._start_session_controller = start_session_controller
        self._session_chat_controller = session_chat_controller
        self._session_management_controller = session_management_controller
        self._file_indexer_service = file_indexer_service
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
    def settings(self) -> "Settings":
        if self._settings is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._settings

    @property
    def project_root(self) -> str:
        if self._project_root is None:
            raise RuntimeError("ServiceContainer not initialized")
        return self._project_root


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


def get_settings() -> "Settings":
    """Get the settings from the container."""
    return _container.settings


def get_project_root() -> str:
    """Get the project root from the container."""
    return _container.project_root
