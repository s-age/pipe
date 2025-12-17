from typing import Any, TypeVar

T = TypeVar("T")


class DependencyContainer:
    """Holds static application dependencies (Services, Repositories).

    Note: This container uses dict[type[Any], Any] to store heterogeneous service types.
    While this sacrifices some type safety, it's an acceptable tradeoff for a generic
    DI container that needs to handle arbitrary service types at runtime.

    The TypeVar T in get() and register() provides type hints at call sites while
    maintaining runtime flexibility. Consider introducing Protocol-based constraints
    if a common interface emerges across registered services in the future.
    """

    def __init__(self) -> None:
        # Acceptable: Generic DI container for heterogeneous service types
        self._services: dict[type[Any], Any] = {}

    def register(self, interface: type[T], instance: T) -> None:
        """Register an instance by its type."""
        self._services[interface] = instance

    def get(self, interface: type[T]) -> T | None:
        """Retrieve an instance by its type."""
        return self._services.get(interface)
