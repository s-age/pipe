"""
Domain logic for Gemini context caching strategy.

Uses actual token counts from API responses (usage_metadata) to make caching decisions.
"""

import logging
from typing import TYPE_CHECKING

from pipe.core.models.prompts.conversation_history import PromptConversationHistory

if TYPE_CHECKING:
    from pipe.core.collections.turns import TurnCollection


class GeminiCache:
    """
    Manages the context caching strategy for Gemini API.

    Strategy (simplified using cached_content_token_count from API):
    - Always create cache when buffered content >= CACHE_UPDATE_THRESHOLD
    - Minimum cache size: 1,024 tokens (2.5 Flash) / 4,096 tokens (2.5 Pro)

    The cache is split into:
    - cached_history: Older turns that are cached (static in API requests)
    - buffered_history: Recent turns that accumulate until next cache threshold
    """

    # Cache update threshold in tokens
    CACHE_UPDATE_THRESHOLD = 20000  # Update cache every 20K tokens

    def __init__(self, tool_response_limit: int = 3):
        """
        Initialize GeminiCache.

        Args:
            tool_response_limit: Maximum tool responses to include per turn
        """
        self.tool_response_limit = tool_response_limit

    def split_history(
        self,
        turns: "TurnCollection",
        cached_content_token_count: int = 0,
        prompt_token_count: int = 0,
    ) -> tuple[PromptConversationHistory | None, PromptConversationHistory | None]:
        """
        Split conversation history into cached and buffered portions.

        Decision logic based on API response metadata:
        - If no cache exists (cached_content_token_count == 0):
          - If buffered content >= CACHE_UPDATE_THRESHOLD: cache all history
          - Otherwise: buffer all history
        - If cache exists (cached_content_token_count > 0):
          - If buffered content >= CACHE_UPDATE_THRESHOLD: expand cache
          - Otherwise: keep current cache boundary

        Args:
            turns: Collection of conversation turns
            cached_content_token_count: From usage_metadata.cached_content_token_count
            prompt_token_count: From usage_metadata.prompt_token_count

        Returns:
            Tuple of (cached_history, buffered_history)
        """
        from pipe.core.domains.turns import get_turns_for_prompt

        # Get all turns in chronological order
        all_turns = list(get_turns_for_prompt(turns, self.tool_response_limit))
        all_turns.reverse()  # Reverse to chronological order (oldest first)

        if not all_turns:
            return None, None

        # Determine cache boundary based on token counts from API
        buffered_tokens = (
            prompt_token_count - cached_content_token_count
            if cached_content_token_count > 0
            else prompt_token_count
        )
        should_update_cache = self.should_update_cache(buffered_tokens)

        if should_update_cache:
            # Cache all history
            cached_turns = all_turns
            buffered_turns = None
            logging.info(
                f"Cache decision: Caching all {len(all_turns)} turns. "
                f"Prompt tokens: {prompt_token_count}, "
                f"Previous cache: {cached_content_token_count}"
            )
        elif cached_content_token_count > 0:
            # We have an existing cache, split based on turn count proportion
            # Use cached_content_token_count to estimate the split point
            cache_ratio = (
                cached_content_token_count / prompt_token_count
                if prompt_token_count > 0
                else 0
            )
            cache_boundary_index = int(len(all_turns) * cache_ratio)

            if cache_boundary_index > 0:
                cached_turns = all_turns[:cache_boundary_index]
                buffered_turns = all_turns[cache_boundary_index:]
            else:
                cached_turns = None
                buffered_turns = all_turns

            logging.info(
                f"Cache decision: Keeping existing cache boundary. "
                f"Cached turns: {len(cached_turns) if cached_turns else 0}, "
                f"Buffered turns: {len(buffered_turns) if buffered_turns else 0}, "
                f"Cached tokens: {cached_content_token_count}, "
                f"Prompt tokens: {prompt_token_count}"
            )
        else:
            # No cache yet and below threshold
            cached_turns = None
            buffered_turns = all_turns
            logging.info(
                f"Cache decision: Below threshold. "
                f"Buffering all {len(all_turns)} turns. "
                f"Prompt tokens: {prompt_token_count}"
            )

        # Build PromptConversationHistory objects
        cached_history = (
            PromptConversationHistory(
                description=(
                    "Cached conversation history from earlier in this session. "
                    "This content is stored in the context cache to optimize "
                    "token usage."
                ),
                turns=cached_turns,
            )
            if cached_turns
            else None
        )

        buffered_history = (
            PromptConversationHistory(
                description=(
                    "Recent conversation history not yet in the cache. "
                    "This will be cached once it reaches the token threshold."
                ),
                turns=buffered_turns,
            )
            if buffered_turns
            else None
        )

        return cached_history, buffered_history

    def should_update_cache(self, buffered_token_count: int) -> bool:
        """
        Determine if the cache should be updated based on buffered token count.

        Args:
            buffered_token_count: Number of tokens not yet cached

        Returns:
            True if buffered tokens exceed threshold
        """
        return buffered_token_count >= self.CACHE_UPDATE_THRESHOLD
