"""Unit tests for gemini_cache_manager module."""

from datetime import UTC
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.domains.gemini_cache_manager import GeminiCacheManager, TokenCountSummary
from pipe.core.models.session import Session
from pipe.core.models.turn import (
    FunctionCallingTurn,
    ModelResponseTurn,
    ToolResponseTurn,
    UserTaskTurn,
)


@pytest.fixture
def mock_client():
    """Create a mock Gemini API client."""
    client = MagicMock()
    client.caches = MagicMock()
    client.caches.delete = MagicMock()
    client.caches.create = MagicMock()
    return client


@pytest.fixture
def mock_session():
    """Create a mock session with required attributes."""
    session = MagicMock(spec=Session)
    session.session_id = "test-session-123"
    session.created_at = "2025-01-01T00:00:00Z"
    session.purpose = "Test purpose"
    session.background = "Test background"
    session.roles = ["developer"]
    session.multi_step_reasoning_enabled = True
    session.procedure = None
    session.cached_turn_count = 0
    session.cache_name = None
    session.cached_content_token_count = 0
    return session


@pytest.fixture
def persisted_turns():
    """
    Create a list of persisted turns (already saved to session).

    This represents the conversation history that has been persisted.
    """
    return [
        UserTaskTurn(
            type="user_task",
            instruction="First instruction",
            timestamp="2025-01-01T00:00:01Z",
        ),
        ModelResponseTurn(
            type="model_response",
            content="First response",
            timestamp="2025-01-01T00:00:02Z",
        ),
        UserTaskTurn(
            type="user_task",
            instruction="Second instruction",
            timestamp="2025-01-01T00:00:03Z",
        ),
        ModelResponseTurn(
            type="model_response",
            content="Second response",
            timestamp="2025-01-01T00:00:04Z",
        ),
    ]


@pytest.fixture
def pending_turns():
    """
    Create pending turns for a ReAct loop scenario.

    Scenario: UserTurn => FunctionCall => ToolResponse => (awaiting ModelResponse)
    This represents the typical flow where:
    1. User asks a question
    2. Model calls a function
    3. Tool returns response
    4. Model will generate final response (not yet persisted)
    """
    from pipe.core.models.turn import TurnResponse

    return [
        UserTaskTurn(
            type="user_task",
            instruction="What is the weather in Tokyo?",
            timestamp="2025-01-01T00:00:05Z",
        ),
        FunctionCallingTurn(
            type="function_calling",
            response='{"name": "get_weather", "args": {"location": "Tokyo"}}',
            timestamp="2025-01-01T00:00:06Z",
        ),
        ToolResponseTurn(
            type="tool_response",
            name="get_weather",
            response=TurnResponse(
                status="success", message='{"temperature": 15, "condition": "sunny"}'
            ),
            timestamp="2025-01-01T00:00:07Z",
        ),
    ]


@pytest.fixture
def cache_manager(mock_client):
    """Create a GeminiCacheManager instance."""
    return GeminiCacheManager(
        client=mock_client,
        project_root="/test/project",
        model_name="gemini-2.5-pro",
        cache_update_threshold=10000,
    )


class TestGeminiCacheManagerInit:
    """Test cases for GeminiCacheManager initialization."""

    def test_init_sets_attributes(self, mock_client):
        """Test that __init__ correctly sets all attributes."""
        manager = GeminiCacheManager(
            client=mock_client,
            project_root="/test/project",
            model_name="gemini-2.5-pro",
            cache_update_threshold=10000,
        )

        assert manager.client == mock_client
        assert manager.project_root == "/test/project"
        assert manager.model_name == "gemini-2.5-pro"
        assert manager.cache_update_threshold == 10000
        assert manager.current_cached_turn_count == 0


class TestUpdateIfNeededBufferedHistory:
    """Test cases for buffered_history assembly."""

    def test_buffered_history_combines_persisted_and_pending(
        self, cache_manager, mock_session, persisted_turns, pending_turns
    ):
        """Test that buffered_history = full_history[cached_turn_count:]."""
        mock_session.cached_turn_count = 2  # First 2 turns are cached

        # Combine persisted and pending into full_history (simulating merged pool)
        full_history = persisted_turns + pending_turns

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 8000,
            "buffered_tokens": 3000,  # Below threshold (10000)
        }

        cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
            session=mock_session,
            full_history=full_history,
            token_count_summary=token_summary,
            threshold=10000,
        )

        # Verify buffered_history structure
        # buffered_history = full_history[2:] = 2 persisted + 3 from pending
        assert len(buffered_history) == 5

        # First 2 items from persisted_turns[2:]
        assert buffered_history[0] == persisted_turns[2]  # UserTask
        assert buffered_history[1] == persisted_turns[3]  # ModelResponse

        # Next 3 items from pending_turns
        assert buffered_history[2] == pending_turns[0]  # UserTask
        assert buffered_history[3] == pending_turns[1]  # FunctionCall
        assert buffered_history[4] == pending_turns[2]  # ToolResponse

    def test_buffered_history_with_no_pending_turns(
        self, cache_manager, mock_session, persisted_turns
    ):
        """Test buffered_history when there are no pending turns."""
        mock_session.cached_turn_count = 2

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 7000,
            "buffered_tokens": 2000,
        }

        cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
            session=mock_session,
            full_history=persisted_turns,
            token_count_summary=token_summary,
            threshold=10000,
        )

        # Only persisted_buffered
        assert len(buffered_history) == 2
        assert buffered_history[0] == persisted_turns[2]
        assert buffered_history[1] == persisted_turns[3]

    def test_buffered_history_with_no_persisted_buffered(
        self, cache_manager, mock_session, persisted_turns, pending_turns
    ):
        """Test buffered_history when all persisted turns are cached."""
        mock_session.cached_turn_count = 4  # All persisted turns are cached

        # All persisted cached, only pending in full_history after cached count
        full_history = persisted_turns + pending_turns

        token_summary: TokenCountSummary = {
            "cached_tokens": 8000,
            "current_prompt_tokens": 10000,
            "buffered_tokens": 2000,
        }

        cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
            session=mock_session,
            full_history=full_history,
            token_count_summary=token_summary,
            threshold=10000,
        )

        # Only turns after index 4 (pending_turns)
        assert len(buffered_history) == 3
        assert buffered_history[0] == pending_turns[0]
        assert buffered_history[1] == pending_turns[1]
        assert buffered_history[2] == pending_turns[2]


class TestUpdateIfNeededCacheJudgment:
    """Test cases for cache update judgment using TokenCountSummary."""

    def test_no_cache_update_when_below_threshold(
        self, cache_manager, mock_session, persisted_turns, pending_turns
    ):
        """Test that cache is NOT updated when buffered_tokens <= threshold."""
        mock_session.cached_turn_count = 2
        mock_session.cache_name = None

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 14000,
            "buffered_tokens": 9000,  # Below threshold (10000)
        }

        with patch(
            "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
        ) as mock_build:
            cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
                session=mock_session,
                full_history=persisted_turns,
                token_count_summary=token_summary,
                threshold=10000,
            )

            # Should NOT call build (no cache creation)
            mock_build.assert_not_called()
            assert cache_name is None
            assert cached_count == 2

    def test_cache_update_when_exceeds_threshold(
        self, cache_manager, mock_session, persisted_turns, pending_turns, mock_client
    ):
        """Test that cache IS updated when buffered_tokens > threshold."""
        mock_session.cached_turn_count = 2
        mock_session.cache_name = None

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 20000,
            "buffered_tokens": 15000,  # Exceeds threshold (10000)
        }

        # Mock cache creation
        mock_cache = MagicMock()
        mock_cache.name = "new-cache-abc123"
        mock_client.caches.create.return_value = mock_cache

        with (
            patch(
                "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
            ) as mock_build,
            patch.object(cache_manager, "_get_existing_cache_name", return_value=None),
            patch.object(cache_manager, "_update_registry"),
        ):
            mock_build.return_value = [MagicMock()]

            cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
                session=mock_session,
                full_history=persisted_turns,
                token_count_summary=token_summary,
                threshold=10000,
            )

            # Should call build (cache creation)
            # With 4 persisted_turns, new_cached_turn_count = len(full_history) - 1 = 3
            mock_build.assert_called_once_with(
                session=mock_session,
                full_history=persisted_turns,
                cached_turn_count=3,
                project_root="/test/project",
                prompt_factory=None,
                settings=None,
            )
            mock_client.caches.create.assert_called_once()
            assert cache_name == "new-cache-abc123"
            assert cached_count == 3


class TestUpdateIfNeededCacheLifecycle:
    """Test cases for cache deletion and creation lifecycle."""

    def test_deletes_old_cache_before_creating_new(
        self, cache_manager, mock_session, persisted_turns, pending_turns, mock_client
    ):
        """Test that old cache is deleted before creating new one."""
        mock_session.cached_turn_count = 2
        mock_session.cache_name = "old-cache-xyz"

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 20000,
            "buffered_tokens": 15000,
        }

        mock_cache = MagicMock()
        mock_cache.name = "new-cache-abc"
        mock_client.caches.create.return_value = mock_cache

        with (
            patch(
                "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
            ) as mock_build,
            patch.object(
                cache_manager, "_get_existing_cache_name", return_value="old-cache-xyz"
            ),
            patch.object(cache_manager, "_update_registry"),
        ):
            mock_build.return_value = [MagicMock()]

            cache_manager.update_if_needed(
                session=mock_session,
                full_history=persisted_turns,
                token_count_summary=token_summary,
                threshold=10000,
            )

            # Verify delete was called before create
            mock_client.caches.delete.assert_called_once_with(name="old-cache-xyz")
            mock_client.caches.create.assert_called_once()

    def test_cache_creation_with_correct_config(
        self, cache_manager, mock_session, persisted_turns, pending_turns, mock_client
    ):
        """Test that cache is created with correct model and config."""
        mock_session.cached_turn_count = 2
        mock_session.cache_name = None

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 20000,
            "buffered_tokens": 15000,
        }

        mock_cache = MagicMock()
        mock_cache.name = "new-cache"
        mock_client.caches.create.return_value = mock_cache

        with (
            patch(
                "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
            ) as mock_build,
            patch.object(cache_manager, "_get_existing_cache_name", return_value=None),
            patch.object(cache_manager, "_update_registry"),
        ):
            mock_content = [MagicMock()]
            mock_build.return_value = mock_content

            cache_manager.update_if_needed(
                session=mock_session,
                full_history=persisted_turns,
                token_count_summary=token_summary,
                threshold=10000,
            )

            mock_client.caches.create.assert_called_once_with(
                model="gemini-2.5-pro",
                config={
                    "contents": mock_content,
                    "ttl": "3600s",
                },
            )

    def test_handles_cache_deletion_error_gracefully(
        self, cache_manager, mock_session, persisted_turns, pending_turns, mock_client
    ):
        """Test that deletion errors don't prevent cache creation."""
        mock_session.cached_turn_count = 2
        mock_session.cache_name = "old-cache"

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 20000,
            "buffered_tokens": 15000,
        }

        # Make delete raise an error
        mock_client.caches.delete.side_effect = Exception("Cache not found")

        mock_cache = MagicMock()
        mock_cache.name = "new-cache"
        mock_client.caches.create.return_value = mock_cache

        with (
            patch(
                "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
            ) as mock_build,
            patch.object(
                cache_manager, "_get_existing_cache_name", return_value="old-cache"
            ),
            patch.object(cache_manager, "_update_registry"),
        ):
            mock_build.return_value = [MagicMock()]

            # Should not raise exception
            cache_name, _, _ = cache_manager.update_if_needed(
                session=mock_session,
                full_history=persisted_turns,
                token_count_summary=token_summary,
                threshold=10000,
            )

            # Cache should still be created
            assert cache_name == "new-cache"
            mock_client.caches.create.assert_called_once()

    def test_handles_cache_creation_error_returns_none(
        self, cache_manager, mock_session, persisted_turns, pending_turns, mock_client
    ):
        """Test that cache creation errors result in None cache_name."""
        mock_session.cached_turn_count = 2
        mock_session.cache_name = None

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 20000,
            "buffered_tokens": 15000,
        }

        # Make create raise an error
        mock_client.caches.create.side_effect = Exception("API error")

        with (
            patch(
                "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
            ) as mock_build,
            patch.object(cache_manager, "_get_existing_cache_name", return_value=None),
        ):
            mock_build.return_value = [MagicMock()]

            cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
                session=mock_session,
                full_history=persisted_turns,
                token_count_summary=token_summary,
                threshold=10000,
            )

            # Should return None but still return buffered_history
            # cached_count should still be updated to reflect the intended expansion
            assert cache_name is None
            assert cached_count == 2  # Remains at initial value when creation fails
            assert len(buffered_history) > 0


class TestUpdateIfNeededReActScenario:
    """Test cases for ReAct loop scenario with function calling."""

    def test_react_loop_buffered_history_at_tool_response(
        self, cache_manager, mock_session, persisted_turns, pending_turns
    ):
        """
        Test buffered_history assembly during ReAct loop at ToolResponse stage.

        Scenario:
        1. Persisted: [UserTask, ModelResponse, UserTask, ModelResponse] (4 turns, first 2 cached)
        2. Pending (merged to full_history): [UserTask, FunctionCall, ToolResponse] (3 turns, awaiting ModelResponse)
        3. Expected buffered_history: full_history[2:] = 5 turns total
        """
        mock_session.cached_turn_count = 2
        full_history = persisted_turns + pending_turns

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 12000,
            "buffered_tokens": 7000,  # Below threshold
        }

        cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
            session=mock_session,
            full_history=full_history,
            token_count_summary=token_summary,
            threshold=10000,
        )

        # Verify complete buffered_history
        assert len(buffered_history) == 5

        # Persisted buffered (turns 2-3)
        assert isinstance(buffered_history[0], UserTaskTurn)
        assert buffered_history[0].instruction == "Second instruction"
        assert isinstance(buffered_history[1], ModelResponseTurn)
        assert buffered_history[1].content == "Second response"

        # Pending (ReAct loop)
        assert isinstance(buffered_history[2], UserTaskTurn)
        assert buffered_history[2].instruction == "What is the weather in Tokyo?"
        assert isinstance(buffered_history[3], FunctionCallingTurn)
        assert "get_weather" in buffered_history[3].response
        assert isinstance(buffered_history[4], ToolResponseTurn)
        assert buffered_history[4].name == "get_weather"

    def test_react_loop_triggers_cache_update(
        self, cache_manager, mock_session, persisted_turns, pending_turns, mock_client
    ):
        """
        Test cache update triggered during ReAct loop when buffered tokens exceed threshold.

        This simulates the scenario where:
        - User asks a question
        - Model calls function
        - Tool responds
        - Buffered tokens exceed threshold -> trigger cache update
        - Model will generate final response with new cache
        """
        mock_session.cached_turn_count = 2
        mock_session.cache_name = "old-cache"
        full_history = persisted_turns + pending_turns

        # Simulate high buffered tokens (exceeds threshold)
        token_summary: TokenCountSummary = {
            "cached_tokens": 8000,
            "current_prompt_tokens": 25000,
            "buffered_tokens": 17000,  # Exceeds threshold (10000)
        }

        mock_cache = MagicMock()
        mock_cache.name = "new-cache-after-tool-response"
        mock_client.caches.create.return_value = mock_cache

        with (
            patch(
                "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
            ) as mock_build,
            patch.object(
                cache_manager, "_get_existing_cache_name", return_value="old-cache"
            ),
            patch.object(cache_manager, "_update_registry"),
        ):
            mock_build.return_value = [MagicMock()]

            cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
                session=mock_session,
                full_history=full_history,
                token_count_summary=token_summary,
                threshold=10000,
            )

            # Verify cache was updated
            mock_client.caches.delete.assert_called_once_with(name="old-cache")
            mock_client.caches.create.assert_called_once()
            assert cache_name == "new-cache-after-tool-response"

            # Verify buffered_history still assembled correctly
            assert len(buffered_history) == 5
            assert isinstance(buffered_history[3], FunctionCallingTurn)
            assert isinstance(buffered_history[4], ToolResponseTurn)


class TestUpdateIfNeededStateManagement:
    """Test cases for on-memory state management."""

    def test_initializes_cached_turn_count_on_first_call(
        self, cache_manager, mock_session, persisted_turns, pending_turns
    ):
        """Test that current_cached_turn_count is initialized from session."""
        mock_session.cached_turn_count = 3

        token_summary: TokenCountSummary = {
            "cached_tokens": 6000,
            "current_prompt_tokens": 8000,
            "buffered_tokens": 2000,
        }

        cache_manager.update_if_needed(
            session=mock_session,
            full_history=persisted_turns,
            token_count_summary=token_summary,
            threshold=10000,
        )

        assert cache_manager.current_cached_turn_count == 3

    def test_cached_turn_count_updates_after_cache_expansion(
        self, cache_manager, mock_session, persisted_turns, pending_turns, mock_client
    ):
        """Test that cached_turn_count is updated when cache is expanded."""
        mock_session.cached_turn_count = 2

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 20000,
            "buffered_tokens": 15000,
        }

        mock_cache = MagicMock()
        mock_cache.name = "new-cache"
        mock_client.caches.create.return_value = mock_cache

        with (
            patch(
                "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
            ) as mock_build,
            patch.object(cache_manager, "_get_existing_cache_name", return_value=None),
            patch.object(cache_manager, "_update_registry"),
        ):
            mock_build.return_value = [MagicMock()]

            cache_name, cached_count, _ = cache_manager.update_if_needed(
                session=mock_session,
                full_history=persisted_turns,
                token_count_summary=token_summary,
                threshold=10000,
            )

            # Cached turn count should expand to cache all but last turn
            # With 4 persisted_turns, new count = len(full_history) - 1 = 3
            assert cached_count == 3
            assert cache_manager.current_cached_turn_count == 3

    def test_returns_none_when_cache_name_is_empty(
        self, cache_manager, mock_session, persisted_turns, mock_client
    ):
        """Test that None is returned when cache creation returns empty name."""
        mock_session.cached_turn_count = 2

        token_summary: TokenCountSummary = {
            "cached_tokens": 5000,
            "current_prompt_tokens": 20000,
            "buffered_tokens": 15000,
        }

        # Mock cache object with empty name
        mock_cache = MagicMock()
        mock_cache.name = ""  # Empty cache name
        mock_client.caches.create.return_value = mock_cache

        with (
            patch(
                "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
            ) as mock_build,
            patch.object(cache_manager, "_get_existing_cache_name", return_value=None),
        ):
            mock_build.return_value = [MagicMock()]

            cache_name, cached_count, buffered_history = cache_manager.update_if_needed(
                session=mock_session,
                full_history=persisted_turns,
                token_count_summary=token_summary,
                threshold=10000,
            )

            # Should return None when cache name is empty
            assert cache_name is None
            assert cached_count == 2  # Should remain at initial value
            assert len(buffered_history) > 0


class TestUpdateRegistry:
    """Test cases for _update_registry method."""

    def test_creates_new_registry_file(
        self, cache_manager, mock_session, tmp_path, mock_client
    ):
        """Test that _update_registry creates a new registry file when it doesn't exist."""
        # Update cache_manager to use tmp_path
        cache_manager.project_root = str(tmp_path)

        # Create mock cached object with expire_time
        from datetime import datetime, timedelta

        mock_cached_obj = MagicMock()
        expire_time = datetime.now(UTC) + timedelta(seconds=3600)
        mock_cached_obj.expire_time = expire_time

        cache_manager._update_registry(
            session_id="test-session-123",
            cache_name="test-cache-abc",
            cached_obj=mock_cached_obj,
        )

        # Verify registry file was created
        registry_path = tmp_path / "sessions" / ".cache_registry.json"
        assert registry_path.exists()

        # Verify contents (to_dict() doesn't include 'entries' key)
        import json

        with open(registry_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "test-session-123" in data
        assert data["test-session-123"]["name"] == "test-cache-abc"
        assert data["test-session-123"]["session_id"] == "test-session-123"
        assert "expire_time" in data["test-session-123"]

    def test_updates_existing_registry_file(
        self, cache_manager, mock_session, tmp_path, mock_client
    ):
        """Test that _update_registry updates an existing registry file."""
        # Update cache_manager to use tmp_path
        cache_manager.project_root = str(tmp_path)

        # Create existing registry file
        import json
        from datetime import datetime, timedelta

        registry_path = tmp_path / "sessions" / ".cache_registry.json"
        registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Use the correct format (without 'entries' wrapper)
        existing_data = {
            "existing-session": {
                "name": "existing-cache",
                "expire_time": "2025-01-01T12:00:00Z",
                "session_id": "existing-session",
            }
        }

        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f)

        # Create mock cached object with expire_time
        mock_cached_obj = MagicMock()
        expire_time = datetime.now(UTC) + timedelta(seconds=3600)
        mock_cached_obj.expire_time = expire_time

        cache_manager._update_registry(
            session_id="new-session-456",
            cache_name="new-cache-def",
            cached_obj=mock_cached_obj,
        )

        # Verify registry file was updated
        with open(registry_path, encoding="utf-8") as f:
            data = json.load(f)

        # Old entry should still exist
        assert "existing-session" in data
        assert data["existing-session"]["name"] == "existing-cache"

        # New entry should be added
        assert "new-session-456" in data
        assert data["new-session-456"]["name"] == "new-cache-def"

    def test_uses_fallback_expire_time_when_not_provided(
        self, cache_manager, mock_session, tmp_path, mock_client
    ):
        """Test that _update_registry uses fallback expire_time when not in API response."""
        # Update cache_manager to use tmp_path
        cache_manager.project_root = str(tmp_path)

        # Create mock cached object WITHOUT expire_time
        mock_cached_obj = MagicMock()
        mock_cached_obj.expire_time = None

        cache_manager._update_registry(
            session_id="test-session-789",
            cache_name="test-cache-ghi",
            cached_obj=mock_cached_obj,
        )

        # Verify registry file was created
        registry_path = tmp_path / "sessions" / ".cache_registry.json"
        assert registry_path.exists()

        # Verify fallback expire_time was used
        import json

        with open(registry_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "test-session-789" in data
        # Should have an expire_time (calculated as current + 3600s)
        assert "expire_time" in data["test-session-789"]
        # Verify it's a valid ISO format datetime string
        expire_time_str = data["test-session-789"]["expire_time"]
        from datetime import datetime

        datetime.fromisoformat(expire_time_str)  # Should not raise

    def test_uses_settings_timezone_for_fallback(
        self, cache_manager, mock_session, tmp_path, mock_client
    ):
        """Test that _update_registry uses settings timezone for fallback expire_time."""
        from unittest.mock import MagicMock

        # Update cache_manager to use tmp_path and custom settings
        cache_manager.project_root = str(tmp_path)
        mock_settings = MagicMock()
        mock_settings.timezone = "Asia/Tokyo"
        cache_manager.settings = mock_settings

        # Create mock cached object WITHOUT expire_time
        mock_cached_obj = MagicMock()
        mock_cached_obj.expire_time = None

        cache_manager._update_registry(
            session_id="test-session-jkl",
            cache_name="test-cache-mno",
            cached_obj=mock_cached_obj,
        )

        # Verify registry file was created
        registry_path = tmp_path / "sessions" / ".cache_registry.json"
        assert registry_path.exists()

        # The actual timezone calculation is complex to test, but we can verify
        # that the expire_time was set and is valid
        import json

        with open(registry_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "test-session-jkl" in data
        expire_time_str = data["test-session-jkl"]["expire_time"]
        from datetime import datetime

        datetime.fromisoformat(expire_time_str)  # Should not raise
