"""Utility functions for Gemini API cache management.

This module provides stateless utility functions for managing Gemini API cache lifecycle.
"""

import json
import os
from datetime import UTC, datetime, timedelta

import google.genai as genai
from google.genai import types
from pipe.core.models.cache_registry import CacheRegistry, CacheRegistryEntry
from pipe.core.utils.datetime import get_current_datetime


def is_cache_expired(
    expire_time_str: str, current_time: datetime | None = None
) -> bool:
    """
    Check if a Gemini API cache has expired.

    Args:
        expire_time_str: ISO 8601 formatted expiration time string (e.g., "2025-01-15T10:30:00+00:00")
        current_time: Comparison baseline time. If None, uses get_current_datetime() (UTC).
                     Can be specified for testing purposes.

    Returns:
        bool: True if expired, False if still valid
    """
    if current_time is None:
        current_time = get_current_datetime()

    try:
        expire_time = datetime.fromisoformat(expire_time_str)
        # If no timezone info, assume UTC
        if expire_time.tzinfo is None:
            expire_time = expire_time.replace(tzinfo=UTC)

        return current_time > expire_time
    except (ValueError, TypeError):
        # If parsing fails, treat as expired
        return True


def get_cache_name_for_session(
    project_root: str,
    session_id: str,
    settings: "Settings | None" = None,  # type: ignore[name-defined] # noqa: F821
) -> str | None:
    """
    Get the cache name for a session from the registry.

    Args:
        project_root: Project root for registry path
        session_id: Session ID
        settings: Application settings (for timezone)

    Returns:
        Cache name (e.g., "cachedContents/xxx") or None if not found or expired
    """
    from zoneinfo import ZoneInfo

    registry_path = os.path.join(project_root, "sessions", ".cache_registry.json")
    cache_registry = _load_registry(registry_path)

    cached_entry = cache_registry.entries.get(session_id)
    if cached_entry:
        # Use user's timezone for cache expiration check
        user_tz = ZoneInfo(settings.timezone) if settings else UTC
        current_time = get_current_datetime(user_tz)
        if not is_cache_expired(cached_entry.expire_time, current_time):
            return cached_entry.name
    return None


def get_or_create_cache(
    client: genai.Client,
    static_content: str,
    model_name: str,
    tools: list[types.Tool],
    project_root: str,
    session_id: str,
    force_create: bool = False,
) -> str | None:
    """
    Get existing cache or create new one for a session.

    Each session can only have one cache at a time. When creating a new cache,
    any existing cache for the same session will be deleted.

    Args:
        client: Gemini API client
        static_content: Static content to cache
        model_name: Model name
        tools: Tool definitions
        project_root: Project root for registry path
        session_id: Session ID that owns this cache
        force_create: If True, delete existing cache and create new one

    Returns:
        Cache name (e.g., "cachedContents/xxx") or None if failed
    """
    registry_path = os.path.join(project_root, "sessions", ".cache_registry.json")

    # Load registry
    cache_registry = _load_registry(registry_path)

    # Clean up expired caches (up to 5 per execution)
    _clean_expired_caches(client, registry_path, cache_registry, limit=5)

    # Check existing cache for this session
    cached_entry = cache_registry.entries.get(session_id)
    if cached_entry and not force_create:
        # Verify it is still valid
        if not is_cache_expired(cached_entry.expire_time) and _verify_cache_exists(
            client, cached_entry.name
        ):
            return cached_entry.name

    # Delete existing cache if present
    if cached_entry:
        _delete_session_cache(client, cache_registry, session_id)
        _save_registry(registry_path, cache_registry)

    # Create new cache
    cache_name = _create_cache(
        client,
        static_content,
        model_name,
        tools,
        session_id,
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


def _delete_session_cache(
    client: genai.Client, cache_registry: CacheRegistry, session_id: str
) -> None:
    """
    Delete all caches belonging to a specific session.

    This enforces the constraint that each session can only have one cache.

    Args:
        client: Gemini API client
        cache_registry: Current registry data
        session_id: Session ID whose caches should be deleted
    """
    entries_to_remove: list[str] = []

    # Find all entries belonging to this session
    for content_hash, entry in cache_registry.entries.items():
        if entry.session_id == session_id:
            try:
                # Delete from API server
                client.caches.delete(name=entry.name)
            except Exception:
                # Ignore errors - cache might already be deleted
                pass

            # Mark for removal from registry
            entries_to_remove.append(content_hash)

    # Remove from registry
    for content_hash in entries_to_remove:
        cache_registry.entries.pop(content_hash, None)


def _clean_expired_caches(
    client: genai.Client,
    registry_path: str,
    cache_registry: CacheRegistry,
    limit: int = 5,
) -> None:
    """
    Clean up expired caches from both API server and local registry.

    Args:
        client: Gemini API client
        registry_path: Path to the registry file
        cache_registry: Current registry data
        limit: Maximum number of caches to delete in one execution (default: 5)
    """
    now = get_current_datetime()
    entries_to_remove: list[str] = []

    # Sort entries by expire_time (oldest first)
    sorted_entries = sorted(
        cache_registry.entries.items(), key=lambda x: x[1].expire_time
    )

    # Process up to 'limit' entries
    count = 0
    for content_hash, entry in sorted_entries:
        if count >= limit:
            break

        # Check if expired
        if is_cache_expired(entry.expire_time, now):
            try:
                # Delete from API server
                client.caches.delete(name=entry.name)
            except Exception as e:
                # NotFound (404) is OK - already deleted
                # For other errors, log warning and continue
                error_str = str(e).lower()
                if "404" not in error_str and "not found" not in error_str:
                    import logging

                    logging.warning(f"Failed to delete cache {entry.name}: {e}")

            # Mark for removal from registry
            entries_to_remove.append(content_hash)
            count += 1

    # Remove from registry
    if entries_to_remove:
        for content_hash in entries_to_remove:
            cache_registry.entries.pop(content_hash, None)
        _save_registry(registry_path, cache_registry)


def _create_cache(
    client: genai.Client,
    static_content: str,
    model_name: str,
    tools: list[types.Tool],
    session_id: str,
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

        # Get expire_time from API response or calculate conservative fallback
        api_expire_time = getattr(cached_obj, "expire_time", None)
        if api_expire_time:
            # Use the accurate expire_time from API
            expire_time_str = api_expire_time.isoformat()
        else:
            # Fallback: Calculate conservative expiration (55 minutes)
            # Safety margin of 300 seconds (5 minutes) to account for clock skew
            fallback_expire_time = get_current_datetime() + timedelta(seconds=3300)
            expire_time_str = fallback_expire_time.isoformat()

        # Update registry: store cache_name by session_id
        cache_registry.entries[session_id] = CacheRegistryEntry(
            name=cache_name,
            expire_time=expire_time_str,
            session_id=session_id,
        )
        _save_registry(registry_path, cache_registry)

        return cache_name
    except Exception:
        return None
