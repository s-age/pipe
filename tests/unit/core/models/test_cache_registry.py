"""Tests for CacheRegistry models."""

import pytest
from pipe.core.models.cache_registry import CacheRegistry, CacheRegistryEntry
from pydantic import ValidationError

from tests.helpers.cache_registry_factory import CacheRegistryFactory


class TestCacheRegistryEntry:
    """Tests for CacheRegistryEntry model."""

    def test_valid_entry_creation(self):
        """Test creating a valid entry."""
        entry = CacheRegistryFactory.create_entry(
            name="cachedContents/abc", expire_time="2025-01-01T00:00:00Z"
        )
        assert entry.name == "cachedContents/abc"
        assert entry.expire_time == "2025-01-01T00:00:00Z"

    def test_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError):
            CacheRegistryEntry(name="cachedContents/abc")  # type: ignore

        with pytest.raises(ValidationError):
            CacheRegistryEntry(expire_time="2025-01-01T00:00:00Z")  # type: ignore

    def test_frozen_config(self):
        """Test that CacheRegistryEntry is frozen."""
        entry = CacheRegistryFactory.create_entry()
        with pytest.raises(
            ValidationError if hasattr(entry, "__pydantic_validator__") else TypeError
        ):
            # In Pydantic V2, frozen models raise ValidationError on assignment if
            # using model_validate.
            # Standard assignment might raise AttributeError or TypeError depending
            # on implementation.
            # Pydantic V2 frozen=True typically raises ValidationError on
            # __setattr__.
            entry.name = "new-name"  # type: ignore


class TestCacheRegistry:
    """Tests for CacheRegistry model."""

    def test_default_values(self):
        """Test default values of CacheRegistry."""
        registry = CacheRegistryFactory.create()
        assert registry.entries == {}

    def test_to_dict(self):
        """Test conversion to dictionary."""
        entry = CacheRegistryFactory.create_entry(name="cache1", expire_time="time1")
        registry = CacheRegistryFactory.create(entries={"hash1": entry})

        expected = {
            "hash1": {
                "name": "cache1",
                "expire_time": "time1",
            }
        }
        assert registry.to_dict() == expected

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "hash1": {
                "name": "cache1",
                "expire_time": "time1",
            }
        }
        registry = CacheRegistry.from_dict(data)
        assert "hash1" in registry.entries
        assert registry.entries["hash1"].name == "cache1"
        assert registry.entries["hash1"].expire_time == "time1"

    def test_model_dump_json(self):
        """Test standard Pydantic serialization."""
        entry = CacheRegistryFactory.create_entry(name="cache1", expire_time="time1")
        registry = CacheRegistryFactory.create(entries={"hash1": entry})

        dumped = registry.model_dump()
        assert dumped["entries"]["hash1"]["name"] == "cache1"

    def test_model_validate(self):
        """Test standard Pydantic deserialization."""
        data = {
            "entries": {
                "hash1": {
                    "name": "cache1",
                    "expire_time": "time1",
                }
            }
        }
        registry = CacheRegistry.model_validate(data)
        assert registry.entries["hash1"].name == "cache1"
