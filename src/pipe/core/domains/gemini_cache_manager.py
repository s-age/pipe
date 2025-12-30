"""
State Management Layer: Cache lifecycle management.

Manages the Gemini API cache lifecycle including update judgment,
delete/create execution, and cached_turn_count management.
"""

from __future__ import annotations

from typing import TypedDict

from google.genai import Client
from pipe.core.domains import gemini_api_static_payload
from pipe.core.models.session import Session
from pipe.core.models.turn import Turn
from pipe.core.utils import gemini_cache_utils


class TokenCountSummary(TypedDict):
    """Token count summary from API response."""

    cached_tokens: int  # Number of tokens in cache
    current_prompt_tokens: int  # Number of tokens in current prompt
    buffered_tokens: int  # Number of tokens in buffered (non-cached) portion


class GeminiCacheManager:
    """
    Manages Gemini API cache lifecycle.

    Handles:
    - Cache update judgment based on buffered token threshold
    - Cache deletion and creation
    - On-memory management of cached_turn_count (distinct from session persistence)
    - Assembly of buffered history (persisted turns not in cache)
    """

    def __init__(
        self,
        client: Client,
        project_root: str,
        model_name: str,
        cache_update_threshold: int,
        prompt_factory: PromptFactory | None = None,  # type: ignore[name-defined] # noqa: F821
        settings: Settings | None = None,  # type: ignore[name-defined] # noqa: F821
    ):
        """
        Initialize the cache manager.

        Args:
            client: Gemini API client for cache operations.
            project_root: Path to project root (for rendering system instruction template).
            model_name: Model identifier (part of cache key).
            cache_update_threshold: Number of buffered tokens before triggering cache update.
            prompt_factory: PromptFactory for generating Prompt objects.
            settings: Application settings.
        """
        self.client = client
        self.project_root = project_root
        self.model_name = model_name
        self.cache_update_threshold = cache_update_threshold
        self.prompt_factory = prompt_factory
        self.settings = settings
        self.current_cached_turn_count: int = 0

    def update_if_needed(
        self,
        session: Session,
        full_history: list[Turn],
        token_count_summary: TokenCountSummary,
        threshold: int,
    ) -> tuple[str | None, int, list[Turn]]:
        """
        Assemble buffered history and determine if cache should be updated.

        Args:
            session: Current session object (for accessing persisted cached_turn_count and cache_name).
            full_history: Complete list of all persisted session turns.
            token_count_summary: Token count information (cached_tokens, current_prompt_tokens, buffered_tokens).
            threshold: Cache update threshold in tokens.

        Returns:
            tuple[str | None, int, list[Turn]]: (cache_name, cached_turn_count, buffered_history)
                - cache_name: Name of the active cache, or None if no cache is used.
                - cached_turn_count: On-memory managed latest cached turn count.
                - buffered_history: Assembled buffered history (persisted turns not in cache).

        Internal Logic:
            1. Initialize: If first call, set current_cached_turn_count from session
            2. Assemble Buffered History: persisted turns from cached_turn_count onwards
            3. Judgment: Use token_count_summary.buffered_tokens for cache update decision
            4. IF buffered_tokens > threshold (Update Flow):
               - Delete old cache if exists
               - Generate new cache content via gemini_api_static_payload.build()
               - Create new cache
               - State remains unchanged (cache recreated with same range)
               - Return (new_cache_name, current_cached_turn_count, buffered_history)
            5. ELSE (Maintain Flow):
               - Return (existing_cache_name, current_cached_turn_count, buffered_history)
        """
        # Step 1: Initialize on first call
        if self.current_cached_turn_count == 0:
            self.current_cached_turn_count = session.cached_turn_count

        # Step 2: Assemble buffered history
        buffered_history = full_history[self.current_cached_turn_count :]

        # Step 3: Judgment - use buffered_tokens from token_count_summary
        buffered_tokens = token_count_summary["buffered_tokens"]

        # Step 4: Update flow if threshold exceeded
        if buffered_tokens > threshold:
            # Calculate new cached_turn_count: cache all except last turn
            new_cached_turn_count = len(full_history) - 1

            # Generate new cache content with new range
            cached_contents = gemini_api_static_payload.build(
                session=session,
                full_history=full_history,
                cached_turn_count=new_cached_turn_count,
                project_root=self.project_root,
                prompt_factory=self.prompt_factory,
                settings=self.settings,
            )

            # Delete old cache if exists (from registry)
            old_cache_name = self._get_existing_cache_name(session.session_id)
            if old_cache_name:
                try:
                    self.client.caches.delete(name=old_cache_name)
                except Exception:
                    # Ignore deletion errors (cache may not exist)
                    pass

            # Create new cache
            try:
                cached_obj = self.client.caches.create(
                    model=self.model_name,
                    config={  # type: ignore[arg-type]
                        "contents": cached_contents,
                        "ttl": "3600s",
                    },
                )
                new_cache_name = cached_obj.name

                # Ensure cache name is valid before updating registry
                if not new_cache_name:
                    return (None, self.current_cached_turn_count, buffered_history)

                # Update registry with new cache
                self._update_registry(session.session_id, new_cache_name, cached_obj)

                # Update state: cache has been expanded
                self.current_cached_turn_count = new_cached_turn_count

                return (
                    new_cache_name,
                    self.current_cached_turn_count,
                    buffered_history,
                )
            except Exception:
                # If cache creation fails, return None (no cache)
                return (None, self.current_cached_turn_count, buffered_history)

        # Step 5: Maintain flow - get existing cache name from registry
        existing_cache_name = self._get_existing_cache_name(session.session_id)
        return (existing_cache_name, self.current_cached_turn_count, buffered_history)

    def _get_existing_cache_name(self, session_id: str) -> str | None:
        """
        Get existing cache name for a session from registry.

        Args:
            session_id: Session ID

        Returns:
            Cache name or None if not found
        """
        return gemini_cache_utils.get_cache_name_for_session(
            project_root=self.project_root,
            session_id=session_id,
        )

    def _update_registry(self, session_id: str, cache_name: str, cached_obj) -> None:
        """
        Update cache registry with new cache entry.

        Args:
            session_id: Session ID
            cache_name: Cache name
            cached_obj: Cached object from API
        """
        import json
        import os
        from datetime import timedelta

        from pipe.core.models.cache_registry import (
            CacheRegistry,
            CacheRegistryEntry,
        )
        from pipe.core.utils.datetime import get_current_datetime

        registry_path = f"{self.project_root}/sessions/.cache_registry.json"

        # Load registry
        if os.path.exists(registry_path):
            with open(registry_path, encoding="utf-8") as f:
                data = json.load(f)
                cache_registry = CacheRegistry.from_dict(data)
        else:
            cache_registry = CacheRegistry()

        # Get expire_time from API response or calculate fallback
        api_expire_time = getattr(cached_obj, "expire_time", None)
        if api_expire_time:
            expire_time_str = api_expire_time.isoformat()
        else:
            fallback_expire_time = get_current_datetime() + timedelta(seconds=3300)
            expire_time_str = fallback_expire_time.isoformat()

        # Update registry
        cache_registry.entries[session_id] = CacheRegistryEntry(
            name=cache_name,
            expire_time=expire_time_str,
            session_id=session_id,
        )

        # Save registry
        os.makedirs(os.path.dirname(registry_path), exist_ok=True)
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(cache_registry.to_dict(), f, indent=2, ensure_ascii=False)
