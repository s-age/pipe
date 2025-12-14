from typing import Any, TypeVar

T = TypeVar("T")


class DependencyContainer:
    """Holds static application dependencies (Services, Repositories)."""

    def __init__(self) -> None:
        self._services: dict[type[Any], Any] = {}

    def register(self, interface: type[T], instance: T) -> None:
        """Register an instance by its type."""
        self._services[interface] = instance

    def get(self, interface: type[T]) -> T | None:
        """Retrieve an instance by its type."""
        return self._services.get(interface)
