"""Factory for creating CacheRegistry test fixtures."""

from pipe.core.models.cache_registry import CacheRegistry, CacheRegistryEntry


class CacheRegistryFactory:
    """Helper class for creating CacheRegistry objects in tests."""

    @staticmethod
    def create_entry(
        name: str = "cachedContents/test-hash",
        expire_time: str = "2025-12-31T23:59:59Z",
        session_id: str = "test-session-id",
    ) -> CacheRegistryEntry:
        """Create a CacheRegistryEntry object."""
        return CacheRegistryEntry(
            name=name, expire_time=expire_time, session_id=session_id
        )

    @staticmethod
    def create(
        entries: dict[str, CacheRegistryEntry] | None = None,
    ) -> CacheRegistry:
        """Create a CacheRegistry object."""
        return CacheRegistry(entries=entries or {})
