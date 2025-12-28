"""Tests for GeminiCache.split_history functionality."""

from pipe.core.domains.gemini_cache import GeminiCache
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn


class TestGeminiCacheSplitHistory:
    """Tests for GeminiCache.split_history method."""

    def test_split_history_with_no_turns(self):
        """Test split_history with empty turn collection."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        result = cache.split_history(
            turns=[],
            cached_content_token_count=0,
            prompt_token_count=0,
            cached_turn_count=0,
        )

        cached_history, buffered_history = result
        assert cached_history is None
        assert buffered_history is None

    def test_split_history_first_turn_no_cache(self):
        """Test split_history with first turn, no existing cache."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        turns = [
            UserTaskTurn(
                type="user_task",
                instruction="First instruction",
                timestamp="2025-01-01T00:00:00+00:00",
            )
        ]

        result = cache.split_history(
            turns=turns,
            cached_content_token_count=0,
            prompt_token_count=1000,
            cached_turn_count=0,
        )

        cached_history, buffered_history = result
        assert cached_history is None
        assert buffered_history is not None
        assert len(buffered_history.turns) == 1

    def test_split_history_should_update_cache(self):
        """Test split_history when buffered tokens exceed threshold."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        turns = [
            UserTaskTurn(
                type="user_task",
                instruction=f"Instruction {i}",
                timestamp="2025-01-01T00:00:00+00:00",
            )
            for i in range(10)
        ]

        result = cache.split_history(
            turns=turns,
            cached_content_token_count=0,
            prompt_token_count=25000,  # Exceeds threshold
            cached_turn_count=0,
        )

        cached_history, buffered_history = result
        # Should cache all but last turn (for thought signature)
        assert cached_history is not None
        assert len(cached_history.turns) == 9
        assert buffered_history is not None
        assert len(buffered_history.turns) == 1

    def test_split_history_keep_existing_cache_boundary(self):
        """Test split_history preserves existing cache boundary when below threshold."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        # Simulate 32 turns total, 31 already cached
        turns = [
            UserTaskTurn(
                type="user_task",
                instruction=f"Instruction {i}",
                timestamp="2025-01-01T00:00:00+00:00",
            )
            for i in range(32)
        ]

        result = cache.split_history(
            turns=turns,
            cached_content_token_count=50000,  # High cache token count
            prompt_token_count=51000,  # Only 1000 new tokens (below threshold)
            cached_turn_count=31,  # 31 turns were cached
        )

        cached_history, buffered_history = result
        # Should keep existing boundary: 31 cached, 1 buffered
        assert cached_history is not None
        assert len(cached_history.turns) == 31
        assert buffered_history is not None
        assert len(buffered_history.turns) == 1

    def test_split_history_cached_turn_count_greater_than_total_turns(self):
        """Test split_history when cached_turn_count > current turn count (turns were deleted)."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        # Only 5 turns exist, but cached_turn_count says 31 were cached
        turns = [
            UserTaskTurn(
                type="user_task",
                instruction=f"Instruction {i}",
                timestamp="2025-01-01T00:00:00+00:00",
            )
            for i in range(5)
        ]

        result = cache.split_history(
            turns=turns,
            cached_content_token_count=50000,
            prompt_token_count=51000,
            cached_turn_count=31,  # More than current turns!
        )

        cached_history, buffered_history = result
        # Should adjust boundary to max(0, len(all_turns) - 1) = 4
        assert cached_history is not None
        assert len(cached_history.turns) == 4
        assert buffered_history is not None
        assert len(buffered_history.turns) == 1

    def test_split_history_cached_turn_count_equals_total_turns(self):
        """Test split_history when cached_turn_count == current turn count."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        turns = [
            UserTaskTurn(
                type="user_task",
                instruction=f"Instruction {i}",
                timestamp="2025-01-01T00:00:00+00:00",
            )
            for i in range(10)
        ]

        result = cache.split_history(
            turns=turns,
            cached_content_token_count=50000,
            prompt_token_count=51000,
            cached_turn_count=10,  # Same as total turns
        )

        cached_history, buffered_history = result
        # Should adjust boundary to 9 (keep at least 1 buffered)
        assert cached_history is not None
        assert len(cached_history.turns) == 9
        assert buffered_history is not None
        assert len(buffered_history.turns) == 1

    def test_split_history_only_one_turn_with_high_cached_turn_count(self):
        """Test split_history with only 1 turn but high cached_turn_count (worst case)."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        turns = [
            UserTaskTurn(
                type="user_task",
                instruction="Single instruction",
                timestamp="2025-01-01T00:00:00+00:00",
            )
        ]

        result = cache.split_history(
            turns=turns,
            cached_content_token_count=50000,
            prompt_token_count=51000,
            cached_turn_count=31,  # Way more than current turns!
        )

        cached_history, buffered_history = result
        # boundary = max(0, 1 - 1) = 0, so cached_turns = None
        assert cached_history is None
        assert buffered_history is not None
        assert len(buffered_history.turns) == 1

    def test_split_history_caching_disabled(self):
        """Test split_history when caching is disabled (threshold = -1)."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=-1)

        turns = [
            UserTaskTurn(
                type="user_task",
                instruction=f"Instruction {i}",
                timestamp="2025-01-01T00:00:00+00:00",
            )
            for i in range(10)
        ]

        result = cache.split_history(
            turns=turns,
            cached_content_token_count=0,
            prompt_token_count=100000,  # Very high token count
            cached_turn_count=0,
        )

        cached_history, buffered_history = result
        # Should buffer all turns (no caching)
        assert cached_history is None
        assert buffered_history is not None
        assert len(buffered_history.turns) == 10

    def test_split_history_with_model_response_turns(self):
        """Test split_history with mixed user and model turns."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        turns = [
            UserTaskTurn(
                type="user_task",
                instruction="User question 1",
                timestamp="2025-01-01T00:00:00+00:00",
            ),
            ModelResponseTurn(
                type="model_response",
                content="Model response 1",
                timestamp="2025-01-01T00:01:00+00:00",
            ),
            UserTaskTurn(
                type="user_task",
                instruction="User question 2",
                timestamp="2025-01-01T00:02:00+00:00",
            ),
            ModelResponseTurn(
                type="model_response",
                content="Model response 2",
                timestamp="2025-01-01T00:03:00+00:00",
            ),
        ]

        result = cache.split_history(
            turns=turns,
            cached_content_token_count=10000,
            prompt_token_count=11000,
            cached_turn_count=2,  # First 2 turns cached
        )

        cached_history, buffered_history = result
        # Should preserve boundary at 2
        assert cached_history is not None
        assert len(cached_history.turns) == 2
        assert cached_history.turns[0].type == "user_task"
        assert cached_history.turns[1].type == "model_response"
        assert buffered_history is not None
        assert len(buffered_history.turns) == 2

    def test_should_update_cache_below_threshold(self):
        """Test should_update_cache returns False when below threshold."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        assert cache.should_update_cache(10000) is False
        assert cache.should_update_cache(19999) is False

    def test_should_update_cache_at_threshold(self):
        """Test should_update_cache returns True at threshold."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        assert cache.should_update_cache(20000) is True

    def test_should_update_cache_above_threshold(self):
        """Test should_update_cache returns True above threshold."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=20000)

        assert cache.should_update_cache(25000) is True
        assert cache.should_update_cache(100000) is True

    def test_should_update_cache_disabled(self):
        """Test should_update_cache returns False when caching is disabled."""
        cache = GeminiCache(tool_response_limit=3, cache_update_threshold=-1)

        assert cache.should_update_cache(0) is False
        assert cache.should_update_cache(100000) is False
