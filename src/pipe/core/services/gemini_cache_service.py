"""Service for managing Gemini API context cache."""

import hashlib
import json
import os
from datetime import datetime, timedelta

import google.genai as genai
from google.genai import types


class GeminiCacheService:
    """
    Manages lifecycle of Gemini API cached content.

    Responsibilities:
    - Create and retrieve API cache objects
    - Manage local cache registry to avoid redundant API calls
    - Handle cache expiration and invalidation
    - Calculate content hashes for cache identification

    Note:
        The local registry (.cache_registry.json) stores cache metadata
        to minimize API calls for cache existence checks.
    """

    def __init__(self, project_root: str):
        """
        Initialize the cache service.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.registry_path = os.path.join(
            project_root, "sessions", ".cache_registry.json"
        )

    def get_cached_content(
        self,
        client: genai.Client,
        static_content: str,
        model_name: str,
        tools: list[types.Tool],
    ) -> str | None:
        """
        Retrieve existing cache name or create a new cache.

        This method manages the full cache lifecycle:
        1. Calculate content hash (static_content + tools)
        2. Check local registry for existing cache
        3. Verify cache validity with API if found in registry
        4. Create new cache if not found or expired
        5. Update local registry with new cache metadata

        Args:
            client: Initialized Gemini API client
            static_content: The system instruction content to cache
            model_name: The model name to use for cache creation
            tools: List of tools to include in the cache

        Returns:
            Cache name (resource ID like "cachedContents/xxx") or None if failed

        Note:
            - Cache TTL is set to 1 hour (3600s)
            - Local expiration is conservative (55 minutes) to avoid edge cases
            - Failed cache operations return None (graceful degradation)
        """
        # Calculate content hash for cache identification
        tools_str = str(tools) if tools else ""
        combined_content = static_content + tools_str
        content_hash = hashlib.md5(combined_content.encode("utf-8")).hexdigest()

        # Load local cache registry
        cache_registry = self._load_registry()

        # Check for existing cache in registry
        cached_info = cache_registry.get(content_hash)
        cache_name = None

        if cached_info:
            cache_name = cached_info.get("name")
            expire_time_str = cached_info.get("expire_time")

            # Check local expiration time
            if expire_time_str:
                expire_time = datetime.fromisoformat(expire_time_str)
                if datetime.now() > expire_time:
                    cache_name = None  # Expired locally

            # Verify cache still exists on API server
            if cache_name:
                if self._verify_cache_exists(client, cache_name):
                    return cache_name
                else:
                    cache_name = None

        # Create new cache if not found or expired
        if not cache_name:
            cache_name = self._create_cache(
                client, static_content, model_name, tools, content_hash, cache_registry
            )

        return cache_name

    def _load_registry(self) -> dict:
        """
        Load the local cache registry from disk.

        Returns:
            Dictionary mapping content hashes to cache metadata
        """
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_registry(self, cache_registry: dict) -> None:
        """
        Save the cache registry to disk.

        Args:
            cache_registry: Dictionary to save
        """
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(cache_registry, f, indent=2)

    def _verify_cache_exists(self, client: genai.Client, cache_name: str) -> bool:
        """
        Verify that a cache exists on the API server.

        Args:
            client: Gemini API client
            cache_name: Cache resource name to verify

        Returns:
            True if cache exists and is valid, False otherwise
        """
        try:
            client.caches.get(name=cache_name)
            return True
        except Exception:
            return False

    def _create_cache(
        self,
        client: genai.Client,
        static_content: str,
        model_name: str,
        tools: list[types.Tool],
        content_hash: str,
        cache_registry: dict,
    ) -> str | None:
        """
        Create a new cache on the API server and update local registry.

        Args:
            client: Gemini API client
            static_content: Content to cache
            model_name: Model to use
            tools: Tools to include in cache
            content_hash: Hash of the content for registry key
            cache_registry: Current registry to update

        Returns:
            Cache name if successful, None otherwise
        """
        try:
            # Create cache with 1 hour TTL
            cached_obj = client.caches.create(
                model=model_name,
                config={
                    "system_instruction": static_content,
                    "tools": tools,  # type: ignore[typeddict-item]
                    "ttl": "3600s",  # 1 hour
                },
            )
            cache_name = cached_obj.name

            # Update local registry with conservative expiration (55 minutes)
            expire_time = datetime.now() + timedelta(minutes=55)
            cache_registry[content_hash] = {
                "name": cache_name,
                "expire_time": expire_time.isoformat(),
            }

            self._save_registry(cache_registry)
            return cache_name

        except Exception:
            return None
