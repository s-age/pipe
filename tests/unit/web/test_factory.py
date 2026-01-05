"""
Unit tests for GenericActionFactory.
"""

from typing import Any, Generic, TypeVar
from unittest.mock import MagicMock

import pytest
from pipe.core.container import DependencyContainer
from pipe.web.factory import GenericActionFactory

T = TypeVar("T")


class MockService:
    """Mock service for testing injection."""

    pass


class MockActionNoInit:
    """Mock action with no __init__."""

    pass


class MockActionWithInit:
    """Mock action with __init__ and dependencies."""

    def __init__(self, service: MockService, name: str, optional: int = 10):
        self.service = service
        self.name = name
        self.optional = optional


class MockActionWithArgsKwargs:
    """Mock action with *args and **kwargs."""

    def __init__(self, service: MockService, *args, **kwargs):
        self.service = service
        self.args = args
        self.kwargs = kwargs


class GenericService(Generic[T]):
    """Mock generic service."""

    pass


class MockActionWithGeneric:
    """Mock action with generic dependency."""

    def __init__(self, service: GenericService[int]):
        self.service = service


class TestGenericActionFactory:
    """Tests for GenericActionFactory."""

    @pytest.fixture
    def container(self) -> MagicMock:
        """Fixture for DependencyContainer."""
        return MagicMock(spec=DependencyContainer)

    @pytest.fixture
    def factory(self, container: MagicMock) -> GenericActionFactory:
        """Fixture for GenericActionFactory."""
        return GenericActionFactory(container)

    def test_init(self, container: MagicMock):
        """Test initialization of GenericActionFactory."""
        factory = GenericActionFactory(container)
        assert factory.container == container

    def test_create_from_container_cache(
        self, factory: GenericActionFactory, container: MagicMock
    ):
        """Test creating an action that is already in the container."""
        mock_instance = MockActionNoInit()
        container.get.return_value = mock_instance

        result = factory.create(MockActionNoInit, {})

        assert result == mock_instance
        container.get.assert_called_once_with(MockActionNoInit)

    def test_create_no_init(self, factory: GenericActionFactory, container: MagicMock):
        """Test creating an action with no __init__ method."""
        container.get.return_value = None

        result = factory.create(MockActionNoInit, {})

        assert isinstance(result, MockActionNoInit)

    def test_create_inject_from_runtime_context_name(
        self, factory: GenericActionFactory, container: MagicMock
    ):
        """Test injecting dependency from runtime_context by name."""
        container.get.return_value = None
        service: MockService = MockService()
        runtime_context = {"service": service, "name": "test-action"}

        result = factory.create(MockActionWithInit, runtime_context)

        assert result.service == service
        assert result.name == "test-action"
        assert result.optional == 10

    def test_create_inject_from_runtime_context_type(
        self, factory: GenericActionFactory, container: MagicMock
    ):
        """Test injecting dependency from runtime_context by type match."""
        container.get.return_value = None
        service: MockService = MockService()
        # Name doesn't match "service", but type matches MockService
        runtime_context = {"some_service": service, "name": "test-action"}

        result = factory.create(MockActionWithInit, runtime_context)

        assert result.service == service
        assert result.name == "test-action"

    def test_create_inject_from_container(
        self, factory: GenericActionFactory, container: MagicMock
    ):
        """Test injecting dependency from DI container."""
        service: MockService = MockService()

        def container_get_side_effect(interface: type[Any]) -> Any | None:
            if interface == MockService:
                return service
            return None

        container.get.side_effect = container_get_side_effect
        runtime_context = {"name": "test-action"}

        result = factory.create(MockActionWithInit, runtime_context)

        assert result.service == service
        assert result.name == "test-action"

    def test_create_inject_default_value(
        self, factory: GenericActionFactory, container: MagicMock
    ):
        """Test using default value for dependency."""
        container.get.return_value = None
        service: MockService = MockService()
        runtime_context = {"service": service, "name": "test-action"}

        result = factory.create(MockActionWithInit, runtime_context)

        assert result.optional == 10

    def test_create_resolution_failure(
        self, factory: GenericActionFactory, container: MagicMock
    ):
        """Test RuntimeError when dependency cannot be resolved."""
        container.get.return_value = None
        runtime_context = {"name": "test-action"}
        # Missing "service" dependency

        with pytest.raises(
            RuntimeError,
            match=r"Cannot resolve dependency 'service: .*' for action 'MockActionWithInit'",
        ):
            factory.create(MockActionWithInit, runtime_context)

    def test_create_ignore_args_kwargs(
        self, factory: GenericActionFactory, container: MagicMock
    ):
        """Test that *args and **kwargs are ignored during injection."""
        container.get.return_value = None
        service: MockService = MockService()
        runtime_context = {"service": service}

        result = factory.create(MockActionWithArgsKwargs, runtime_context)

        assert result.service == service
        assert result.args == ()
        assert result.kwargs == {}

    def test_create_generic_type_match(
        self, factory: GenericActionFactory, container: MagicMock
    ):
        """Test injecting dependency with generic type match."""
        container.get.return_value = None
        service: GenericService[int] = GenericService()
        runtime_context = {"some_generic": service}

        result = factory.create(MockActionWithGeneric, runtime_context)

        assert result.service == service

    def test_create_type_hints_exception_handling(
        self,
        factory: GenericActionFactory,
        container: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Test handling of exceptions during get_type_hints."""
        container.get.return_value = None

        from pipe.web import factory as factory_module

        def mock_get_type_hints(obj: Any) -> dict[str, Any]:
            raise Exception("Type hint error")

        monkeypatch.setattr(factory_module, "get_type_hints", mock_get_type_hints)

        # MockActionNoInit has no type hints needed, but we check if it proceeds
        result = factory.create(MockActionNoInit, {})
        assert isinstance(result, MockActionNoInit)

        # For MockActionWithInit, it should still resolve by name if provided in runtime_context
        service: MockService = MockService()
        runtime_context = {"service": service, "name": "test"}
        result = factory.create(MockActionWithInit, runtime_context)
        assert result.service == service
        assert result.name == "test"
