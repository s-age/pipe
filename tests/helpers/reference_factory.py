"""Factory for creating Reference test fixtures."""

from pipe.core.models.reference import Reference


class ReferenceFactory:
    """Helper class for creating Reference objects in tests."""

    @staticmethod
    def create(
        path: str = "test.py",
        disabled: bool = False,
        ttl: int | None = None,
        persist: bool = False,
        **kwargs,
    ) -> Reference:
        """Create a Reference object with default test values."""
        return Reference(
            path=path, disabled=disabled, ttl=ttl, persist=persist, **kwargs
        )

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[Reference]:
        """Create multiple Reference objects."""
        return [
            ReferenceFactory.create(path=f"test_{i}.py", **kwargs) for i in range(count)
        ]
