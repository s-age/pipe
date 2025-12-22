"""Factory for creating Artifact test fixtures."""

from pipe.core.models.artifact import Artifact


class ArtifactFactory:
    """Helper class for creating Artifact objects in tests."""

    @staticmethod
    def create(
        path: str = "test.py", contents: str | None = "print('hello')", **kwargs
    ) -> Artifact:
        """Create an Artifact object with default test values."""
        return Artifact(path=path, contents=contents, **kwargs)

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[Artifact]:
        """Create multiple Artifact objects."""
        return [
            ArtifactFactory.create(path=f"test_{i}.py", **kwargs) for i in range(count)
        ]
