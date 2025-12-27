"""Utility functions for Gemini API cache management.

This module provides stateless utility functions for managing Gemini API cache lifecycle.
"""

import hashlib
import json
import os
from datetime import datetime, timedelta

import google.genai as genai
from google.genai import types
from pipe.core.models.cache_registry import CacheRegistry, CacheRegistryEntry


def get_or_create_cache(
    client: genai.Client,
    static_content: str,
    model_name: str,
    tools: list[types.Tool],
    project_root: str,
) -> str | None:
    """
    Get existing cache or create new one.

    Args:
        client: Gemini API client
        static_content: Static content to cache
        model_name: Model name
        tools: Tool definitions
        project_root: Project root for registry path

    Returns:
        Cache name (e.g., "cachedContents/xxx") or None if failed
    """
    registry_path = os.path.join(project_root, "sessions", ".cache_registry.json")

    # Calculate content hash
    tools_str = str(tools) if tools else ""
    combined_content = static_content + tools_str
    content_hash = hashlib.md5(combined_content.encode("utf-8")).hexdigest()

    # Load registry
    cache_registry = _load_registry(registry_path)

    # Check existing cache
    cached_entry = cache_registry.entries.get(content_hash)
    if cached_entry:
        cache_name = cached_entry.name
        expire_time = datetime.fromisoformat(cached_entry.expire_time)

        # Check if still valid
        if datetime.now() <= expire_time and _verify_cache_exists(client, cache_name):
            return cache_name

    # Create new cache
    cache_name = _create_cache(
        client,
        static_content,
        model_name,
        tools,
        content_hash,
        cache_registry,
        registry_path,
    )
    return cache_name


def _load_registry(registry_path: str) -> CacheRegistry:
    """Load cache registry from disk."""
    if os.path.exists(registry_path):
        try:
            with open(registry_path, encoding="utf-8") as f:
                data = json.load(f)
                return CacheRegistry.from_dict(data)
        except Exception:
            pass
    return CacheRegistry()


def _save_registry(registry_path: str, cache_registry: CacheRegistry) -> None:
    """Save cache registry to disk."""
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(cache_registry.to_dict(), f, indent=2, ensure_ascii=False)


def _verify_cache_exists(client: genai.Client, cache_name: str) -> bool:
    """Verify cache exists on API server."""
    try:
        client.caches.get(name=cache_name)
        return True
    except Exception:
        return False


def _create_cache(
    client: genai.Client,
    static_content: str,
    model_name: str,
    tools: list[types.Tool],
    content_hash: str,
    cache_registry: CacheRegistry,
    registry_path: str,
) -> str | None:
    """Create new cache and update registry."""
    try:
        # Create cache with 1 hour TTL
        cached_obj = client.caches.create(
            model=model_name,
            config={  # type: ignore[arg-type]
                "system_instruction": static_content,
                # Convert Tool objects to dict for compatibility
                "tools": [tool.model_dump() for tool in tools],  # type: ignore[misc]
                "ttl": "3600s",  # 1 hour
            },
        )
        cache_name = cached_obj.name

        # Update registry
        expire_time = datetime.now() + timedelta(minutes=55)  # Conservative
        cache_registry.entries[content_hash] = CacheRegistryEntry(
            name=cache_name,
            expire_time=expire_time.isoformat(),
        )
        _save_registry(registry_path, cache_registry)

        return cache_name
    except Exception:
        return None
