"""Unit tests for ServiceContainer in service_container.py."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pipe.web.service_container import (
    ServiceContainer,
    get_container,
    get_file_indexer_service,
    get_procedure_service,
    get_project_root,
    get_role_service,
    get_search_sessions_service,
    get_session_artifact_service,
    get_session_chat_controller,
    get_session_management_controller,
    get_session_management_service,
    get_session_meta_service,
    get_session_optimization_service,
    get_session_reference_service,
    get_session_service,
    get_session_todo_service,
    get_session_tree_service,
    get_session_turn_service,
    get_session_workflow_service,
    get_settings,
    get_start_session_controller,
)


class TestServiceContainer:
    """Tests for the ServiceContainer class."""

    @pytest.fixture
    def container(self) -> ServiceContainer:
        """Create a fresh ServiceContainer instance for each test."""
        return ServiceContainer()

    @pytest.fixture
    def mock_services(self) -> dict[str, Any]:
        """Create a dictionary of mock services."""
        return {
            "session_service": MagicMock(),
            "session_management_service": MagicMock(),
            "session_tree_service": MagicMock(),
            "session_workflow_service": MagicMock(),
            "session_optimization_service": MagicMock(),
            "session_reference_service": MagicMock(),
            "session_artifact_service": MagicMock(),
            "session_turn_service": MagicMock(),
            "session_meta_service": MagicMock(),
            "session_todo_service": MagicMock(),
            "start_session_controller": MagicMock(),
            "session_chat_controller": MagicMock(),
            "session_management_controller": MagicMock(),
            "file_indexer_service": MagicMock(),
            "search_sessions_service": MagicMock(),
            "procedure_service": MagicMock(),
            "role_service": MagicMock(),
            "settings": MagicMock(),
            "project_root": "/mock/root",
        }

    def test_uninitialized_access(self, container: ServiceContainer):
        """Test that accessing properties before initialization raises RuntimeError."""
        properties = [
            "session_service",
            "session_management_service",
            "session_tree_service",
            "session_workflow_service",
            "session_optimization_service",
            "session_reference_service",
            "session_artifact_service",
            "session_turn_service",
            "session_meta_service",
            "session_todo_service",
            "start_session_controller",
            "session_chat_controller",
            "session_management_controller",
            "file_indexer_service",
            "search_sessions_service",
            "settings",
            "project_root",
            "procedure_service",
            "role_service",
        ]

        for prop in properties:
            with pytest.raises(RuntimeError, match="ServiceContainer not initialized"):
                getattr(container, prop)

    def test_init_sets_all_services(
        self, container: ServiceContainer, mock_services: dict[str, MagicMock]
    ):
        """Test that init correctly sets all services and properties return them."""
        container.init(**mock_services)

        assert container.session_service == mock_services["session_service"]
        assert (
            container.session_management_service
            == mock_services["session_management_service"]
        )
        assert container.session_tree_service == mock_services["session_tree_service"]
        assert (
            container.session_workflow_service
            == mock_services["session_workflow_service"]
        )
        assert (
            container.session_optimization_service
            == mock_services["session_optimization_service"]
        )
        assert (
            container.session_reference_service
            == mock_services["session_reference_service"]
        )
        assert (
            container.session_artifact_service
            == mock_services["session_artifact_service"]
        )
        assert container.session_turn_service == mock_services["session_turn_service"]
        assert container.session_meta_service == mock_services["session_meta_service"]
        assert container.session_todo_service == mock_services["session_todo_service"]
        assert (
            container.start_session_controller
            == mock_services["start_session_controller"]
        )
        assert (
            container.session_chat_controller
            == mock_services["session_chat_controller"]
        )
        assert (
            container.session_management_controller
            == mock_services["session_management_controller"]
        )
        assert container.file_indexer_service == mock_services["file_indexer_service"]
        assert (
            container.search_sessions_service
            == mock_services["search_sessions_service"]
        )
        assert container.settings == mock_services["settings"]
        assert container.project_root == mock_services["project_root"]
        assert container.procedure_service == mock_services["procedure_service"]
        assert container.role_service == mock_services["role_service"]


class TestGlobalHelpers:
    """Tests for the global helper functions."""

    @pytest.fixture
    def mock_container(self):
        """Mock the global _container instance."""
        with patch("pipe.web.service_container._container") as mock:
            yield mock

    def test_get_container(self, mock_container: MagicMock):
        """Test get_container returns the global instance."""
        assert get_container() == mock_container

    def test_get_session_service(self, mock_container: MagicMock):
        """Test get_session_service delegates to container."""
        get_session_service()
        # Accessing the property triggers the getter
        _ = mock_container.session_service

    def test_all_get_helpers(self, mock_container: MagicMock):
        """Test all helper functions delegate to the correct container property."""
        helpers = [
            (get_session_service, "session_service"),
            (get_session_management_service, "session_management_service"),
            (get_session_tree_service, "session_tree_service"),
            (get_session_workflow_service, "session_workflow_service"),
            (get_session_optimization_service, "session_optimization_service"),
            (get_session_reference_service, "session_reference_service"),
            (get_session_artifact_service, "session_artifact_service"),
            (get_session_turn_service, "session_turn_service"),
            (get_session_meta_service, "session_meta_service"),
            (get_session_todo_service, "session_todo_service"),
            (get_start_session_controller, "start_session_controller"),
            (get_session_chat_controller, "session_chat_controller"),
            (get_session_management_controller, "session_management_controller"),
            (get_file_indexer_service, "file_indexer_service"),
            (get_search_sessions_service, "search_sessions_service"),
            (get_settings, "settings"),
            (get_project_root, "project_root"),
            (get_procedure_service, "procedure_service"),
            (get_role_service, "role_service"),
        ]

        for helper_func, prop_name in helpers:
            # Reset mock to clear previous accesses
            mock_container.reset_mock()

            # Call the helper
            result = helper_func()

            # Verify the property was accessed on the container
            expected_mock = getattr(mock_container, prop_name)
            assert result == expected_mock
