"""Pydantic models for Gemini cache registry."""

from pydantic import BaseModel, ConfigDict, Field


class CacheRegistryEntry(BaseModel):
    """Single entry in the cache registry."""

    name: str = Field(description="Cache resource name (e.g., 'cachedContents/xxx')")
    expire_time: str = Field(description="ISO format expiration timestamp")
    session_id: str = Field(description="Session ID that owns this cache")

    model_config = ConfigDict(frozen=True)


class CacheRegistry(BaseModel):
    """Registry mapping content hashes to cache metadata."""

    # Mapping from content hash to cache entry
    # Using dict[str, CacheRegistryEntry] for type safety
    entries: dict[str, CacheRegistryEntry] = Field(
        default_factory=dict, description="Cache entries keyed by content hash"
    )

    model_config = ConfigDict(frozen=False)  # Allow modification

    def to_dict(self) -> dict[str, dict[str, str]]:
        """Convert to plain dict for JSON serialization."""
        return {
            hash_key: entry.model_dump() for hash_key, entry in self.entries.items()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CacheRegistry":
        """Create from plain dict loaded from JSON."""
        entries = {
            hash_key: CacheRegistryEntry(**entry_data)
            for hash_key, entry_data in data.items()
        }
        return cls(entries=entries)
