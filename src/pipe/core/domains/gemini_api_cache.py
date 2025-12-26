"""
Cache management for Gemini API.

Handles cache creation, retrieval, and content preparation for the Gemini API.
"""

import hashlib
import json
import os
import zoneinfo
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import google.genai as genai
from google.genai import types
from pipe.core.models.cache_registry import CacheRegistry, CacheRegistryEntry
from pipe.core.utils.datetime import get_current_datetime

if TYPE_CHECKING:
    from pipe.core.domains.gemini_cache import GeminiCache
    from pipe.core.models.settings import Settings


class GeminiApiCacheManager:
    """
    Manages lifecycle of Gemini API cached content.

    Responsibilities:
    - Create and retrieve API cache objects
    - Manage local cache registry to avoid redundant API calls
    - Handle cache expiration and invalidation
    - Calculate content hashes for cache identification
    - Prepare content for API calls based on cache strategy

    Note:
        The local registry (.cache_registry.json) stores cache metadata
        to minimize API calls for cache existence checks.
    """

    def __init__(self, project_root: str, settings: "Settings"):
        """
        Initialize the cache manager.

        Args:
            project_root: Root directory of the project
            settings: Settings object for timezone configuration
        """
        self.project_root = project_root
        self.registry_path = os.path.join(
            project_root, "sessions", ".cache_registry.json"
        )

        # Convert timezone string to ZoneInfo object
        try:
            self.timezone = zoneinfo.ZoneInfo(settings.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            # Fallback to UTC if timezone not found
            self.timezone = zoneinfo.ZoneInfo("UTC")

    def prepare_cache_and_content(
        self,
        client: genai.Client,
        gemini_cache: "GeminiCache",
        session_data,
        static_content: str,
        dynamic_content: str,
        converted_tools: list[types.Tool],
        buffered_history_contents: list[types.Content],
        current_task_content: types.Content | None,
        model_name: str,
        streaming_log_repo,
    ) -> tuple[str | None, list[types.Content | str]]:
        """
        Determine cache strategy and prepare content to send.

        Args:
            client: Gemini API client
            gemini_cache: Cache domain logic
            session_data: Current session data
            static_content: Static prompt content
            dynamic_content: Dynamic prompt content
            converted_tools: Converted tool definitions
            buffered_history_contents: List of buffered turns as Content objects
            current_task_content: Content object for the current task (optional)
            model_name: Model name for cache creation
            streaming_log_repo: Repository for logging cache decisions

        Returns:
            Tuple of (cached_content_name, content_list_to_send)
        """
        # Calculate buffered tokens (not yet cached)
        buffered_tokens = (
            session_data.token_count - session_data.cached_content_token_count
            if session_data.cached_content_token_count > 0
            else session_data.token_count
        )

        should_cache = gemini_cache.should_update_cache(buffered_tokens)

        cached_content_name = None
        content_to_send: list[types.Content | str] = []

        if should_cache and static_content:
            # Create/update cache
            cache_msg = (
                f"Cache decision: CREATING/UPDATING cache. "
                f"Current cached_tokens={session_data.cached_content_token_count}, "
                f"Current prompt_tokens={session_data.token_count}, "
                f"Buffered tokens={buffered_tokens}"
            )
            streaming_log_repo.write_log_line(
                "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
            )

            cached_content_name = self.get_cached_content(
                client,
                static_content,
                model_name,
                converted_tools,
            )

        elif not session_data.cached_content_token_count:
            # No cache exists, below threshold: send all
            cache_msg = (
                f"Cache decision: NO CACHE (below threshold). "
                f"Current prompt_tokens={session_data.token_count}, "
                f"Threshold={gemini_cache.cache_update_threshold}. "
                f"Sending static + dynamic content"
            )
            streaming_log_repo.write_log_line(
                "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
            )
            if static_content:
                content_to_send.append(static_content)

        else:
            # Use existing cache
            cache_msg = (
                f"Cache decision: USING EXISTING cache (buffered below threshold). "
                f"Current cached_tokens={session_data.cached_content_token_count}, "
                f"Current prompt_tokens={session_data.token_count}, "
                f"Buffered tokens={buffered_tokens}, "
                f"Threshold={gemini_cache.cache_update_threshold}"
            )
            streaming_log_repo.write_log_line(
                "CACHE_DECISION", cache_msg, get_current_datetime(self.timezone)
            )

            if static_content:
                try:
                    cached_content_name = self.get_cached_content(
                        client,
                        static_content,
                        model_name,
                        converted_tools,
                    )
                except Exception:
                    # Fallback if cache retrieval fails
                    content_to_send.append(static_content)

        # Order: Dynamic (Context) -> Buffered History -> Current Task
        content_to_send.append(dynamic_content)
        content_to_send.extend(buffered_history_contents)
        if current_task_content:
            content_to_send.append(current_task_content)

        return cached_content_name, content_to_send

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
        cached_entry = cache_registry.entries.get(content_hash)
        cache_name = None

        if cached_entry:
            cache_name = cached_entry.name
            expire_time_str = cached_entry.expire_time

            # Check local expiration time
            expire_time = datetime.fromisoformat(expire_time_str)
            if get_current_datetime(self.timezone) > expire_time:
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

    def _load_registry(self) -> CacheRegistry:
        """
        Load the local cache registry from disk.

        Returns:
            CacheRegistry model with cache entries
        """
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, encoding="utf-8") as f:
                    data = json.load(f)
                    return CacheRegistry.from_dict(data)
            except Exception:
                pass
        return CacheRegistry()

    def _save_registry(self, cache_registry: CacheRegistry) -> None:
        """
        Save the cache registry to disk.

        Args:
            cache_registry: CacheRegistry model to save
        """
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(cache_registry.to_dict(), f, indent=2)

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
        cache_registry: CacheRegistry,
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
                config={  # type: ignore[arg-type]
                    "system_instruction": static_content,
                    # Convert Tool objects to dict for compatibility
                    "tools": [tool.model_dump() for tool in tools],  # type: ignore[misc]
                    "ttl": "3600s",  # 1 hour
                },
            )
            cache_name = cached_obj.name

            # Update local registry with conservative expiration (55 minutes)
            expire_time = get_current_datetime(self.timezone) + timedelta(minutes=55)
            cache_registry.entries[content_hash] = CacheRegistryEntry(
                name=cache_name,
                expire_time=expire_time.isoformat(),
            )

            self._save_registry(cache_registry)
            return cache_name

        except Exception:
            return None
