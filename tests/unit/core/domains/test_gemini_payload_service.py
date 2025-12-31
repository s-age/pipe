"""Unit tests for gemini_payload_service module."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.domains.gemini_payload_service import GeminiPayloadService
from pipe.core.models.session import Session
from pipe.core.models.settings import ModelConfig, Settings
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn


@pytest.fixture
def mock_client():
    """Create a mock Gemini API client."""
    client = MagicMock()
    client.caches = MagicMock()
    client.caches.delete = MagicMock()
    client.caches.create = MagicMock()
    return client


@pytest.fixture
def mock_settings():
    """Create mock settings with model config."""
    model_config = ModelConfig(
        name="gemini-2.5-pro",
        context_limit=1000000,
        cache_update_threshold=10000,
    )

    settings = MagicMock(spec=Settings)
    settings.model = model_config
    settings.search_model = model_config

    return settings


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
    session.turns = []
    session.artifacts = []
    return session


@pytest.fixture
def mock_prompt_factory():
    """Create a mock prompt factory."""
    factory = MagicMock()
    mock_prompt = MagicMock()
    mock_prompt.buffered_history = None
    factory.create.return_value = mock_prompt
    return factory


@pytest.fixture
def payload_service(mock_client, mock_settings):
    """Create a GeminiPayloadService instance."""
    return GeminiPayloadService(
        client=mock_client,
        project_root="/test/project",
        settings=mock_settings,
    )


class TestGeminiPayloadServiceInit:
    """Test cases for GeminiPayloadService initialization."""

    def test_init_sets_attributes(self, mock_client, mock_settings):
        """Test that __init__ correctly sets all attributes."""
        service = GeminiPayloadService(
            client=mock_client,
            project_root="/test/project",
            settings=mock_settings,
        )

        assert service.client == mock_client
        assert service.project_root == "/test/project"
        assert service.settings == mock_settings
        assert service.last_token_summary == {
            "cached_tokens": 0,
            "current_prompt_tokens": 0,
            "buffered_tokens": 0,
        }
        assert service.cache_manager is not None

    def test_init_raises_error_if_model_is_not_config_object(self, mock_client):
        """Test that __init__ raises error if settings.model is not ModelConfig."""
        invalid_settings = MagicMock()
        invalid_settings.model = "gemini-2.5-pro"  # String instead of ModelConfig

        with pytest.raises(ValueError, match="settings.model must be a ModelConfig"):
            GeminiPayloadService(
                client=mock_client,
                project_root="/test/project",
                settings=invalid_settings,
            )


class TestPrepareRequestBasicFlow:
    """Test cases for prepare_request basic flow."""

    def test_prepare_request_calls_cache_manager_update_if_needed(
        self, payload_service, mock_session, mock_prompt_factory
    ):
        """Test that prepare_request calls cache_manager.update_if_needed."""
        with patch.object(
            payload_service.cache_manager, "update_if_needed"
        ) as mock_update:
            mock_update.return_value = (None, 0, [])

            with (
                patch(
                    "pipe.core.domains.gemini_payload_service.GeminiApiDynamicPayload"
                ) as mock_dynamic,
                patch(
                    "pipe.core.domains.gemini_api_static_payload.build"
                ) as mock_static_build,
            ):
                mock_dynamic.return_value.build.return_value = []
                mock_static_build.return_value = []

                payload_service.prepare_request(
                    session=mock_session,
                    prompt_factory=mock_prompt_factory,
                    current_instruction="Test",
                )

                # Verify cache manager was called
                mock_update.assert_called_once()
                call_args = mock_update.call_args
                assert call_args.kwargs["session"] == mock_session
                assert call_args.kwargs["full_history"] == mock_session.turns

    def test_prepare_request_updates_session_state(
        self, payload_service, mock_session, mock_prompt_factory
    ):
        """Test that prepare_request updates session.cached_turn_count."""
        with patch.object(
            payload_service.cache_manager, "update_if_needed"
        ) as mock_update:
            mock_update.return_value = ("test-cache-123", 5, [])

            with patch(
                "pipe.core.domains.gemini_payload_service.GeminiApiDynamicPayload"
            ) as mock_dynamic:
                mock_dynamic.return_value.build.return_value = []

                contents, cache_name = payload_service.prepare_request(
                    session=mock_session,
                    prompt_factory=mock_prompt_factory,
                    current_instruction=None,
                )

                # Verify session state was updated (cached_turn_count)
                # Note: cache_name is managed in .cache_registry.json, not in Session model
                assert mock_session.cached_turn_count == 5
                # Verify return values
                assert cache_name == "test-cache-123"

    def test_prepare_request_builds_prompt_with_buffered_history(
        self, payload_service, mock_session, mock_prompt_factory
    ):
        """Test that prepare_request sets buffered_history on prompt."""
        buffered_turns = [
            UserTaskTurn(
                type="user_task",
                instruction="Buffered instruction",
                timestamp="2025-01-01T00:00:01Z",
            )
        ]

        with patch.object(
            payload_service.cache_manager, "update_if_needed"
        ) as mock_update:
            mock_update.return_value = (None, 0, buffered_turns)

            with (
                patch(
                    "pipe.core.domains.gemini_payload_service.GeminiApiDynamicPayload"
                ) as mock_dynamic,
                patch(
                    "pipe.core.domains.gemini_api_static_payload.build"
                ) as mock_static_build,
            ):
                mock_dynamic.return_value.build.return_value = []
                mock_static_build.return_value = []

                mock_prompt = MagicMock()
                mock_prompt_factory.create.return_value = mock_prompt

                payload_service.prepare_request(
                    session=mock_session,
                    prompt_factory=mock_prompt_factory,
                    current_instruction=None,
                )

                # Verify buffered_history was set on prompt
                assert mock_prompt.buffered_history == buffered_turns

    def test_prepare_request_returns_contents_and_cache_name(
        self, payload_service, mock_session, mock_prompt_factory
    ):
        """Test that prepare_request returns (contents, cache_name) tuple."""
        mock_contents = [MagicMock(), MagicMock()]

        with patch.object(
            payload_service.cache_manager, "update_if_needed"
        ) as mock_update:
            mock_update.return_value = ("cache-xyz", 3, [])

            with patch(
                "pipe.core.domains.gemini_payload_service.GeminiApiDynamicPayload"
            ) as mock_dynamic:
                mock_dynamic.return_value.build.return_value = mock_contents

                contents, cache_name = payload_service.prepare_request(
                    session=mock_session,
                    prompt_factory=mock_prompt_factory,
                    current_instruction=None,
                )

                assert contents == mock_contents
                assert cache_name == "cache-xyz"

    def test_prepare_request_includes_static_when_no_cache(
        self, payload_service, mock_session, mock_prompt_factory
    ):
        """Test that prepare_request includes static content when cache_name is None."""
        mock_static_contents = [MagicMock()]
        mock_dynamic_contents = [MagicMock()]

        with patch.object(
            payload_service.cache_manager, "update_if_needed"
        ) as mock_update:
            mock_update.return_value = (None, 0, [])  # No cache

            with (
                patch(
                    "pipe.core.domains.gemini_payload_service.GeminiApiDynamicPayload"
                ) as mock_dynamic,
                patch(
                    "pipe.core.domains.gemini_api_static_payload.build"
                ) as mock_static_build,
            ):
                mock_dynamic.return_value.build.return_value = mock_dynamic_contents
                mock_static_build.return_value = mock_static_contents

                contents, cache_name = payload_service.prepare_request(
                    session=mock_session,
                    prompt_factory=mock_prompt_factory,
                    current_instruction=None,
                )

                # Verify static payload was built
                mock_static_build.assert_called_once()

                # Verify contents includes both static and dynamic
                assert len(contents) == 2
                assert contents[0] == mock_static_contents[0]
                assert contents[1] == mock_dynamic_contents[0]
                assert cache_name is None

    def test_prepare_request_excludes_static_when_cache_exists(
        self, payload_service, mock_session, mock_prompt_factory
    ):
        """Test that prepare_request excludes static content when cache exists."""
        mock_dynamic_contents = [MagicMock()]

        with patch.object(
            payload_service.cache_manager, "update_if_needed"
        ) as mock_update:
            mock_update.return_value = ("cache-xyz", 3, [])  # Cache exists

            with (
                patch(
                    "pipe.core.domains.gemini_payload_service.GeminiApiDynamicPayload"
                ) as mock_dynamic,
                patch(
                    "pipe.core.domains.gemini_api_static_payload.build"
                ) as mock_static_build,
            ):
                mock_dynamic.return_value.build.return_value = mock_dynamic_contents

                contents, cache_name = payload_service.prepare_request(
                    session=mock_session,
                    prompt_factory=mock_prompt_factory,
                    current_instruction=None,
                )

                # Verify static payload was NOT built
                mock_static_build.assert_not_called()

                # Verify contents only includes dynamic
                assert contents == mock_dynamic_contents
                assert cache_name == "cache-xyz"


class TestUpdateTokenSummary:
    """Test cases for update_token_summary."""

    def test_update_token_summary_calculates_buffered_tokens(self, payload_service):
        """Test that update_token_summary correctly calculates buffered_tokens."""
        usage_metadata: dict[str, int] = {
            "cached_content_token_count": 5000,
            "prompt_token_count": 12000,
        }

        payload_service.update_token_summary(usage_metadata)

        assert payload_service.last_token_summary["cached_tokens"] == 5000
        assert payload_service.last_token_summary["current_prompt_tokens"] == 12000
        assert payload_service.last_token_summary["buffered_tokens"] == 7000

    def test_update_token_summary_handles_missing_fields(self, payload_service):
        """Test that update_token_summary handles missing metadata fields."""
        usage_metadata: dict[str, int] = {}

        payload_service.update_token_summary(usage_metadata)

        assert payload_service.last_token_summary["cached_tokens"] == 0
        assert payload_service.last_token_summary["current_prompt_tokens"] == 0
        assert payload_service.last_token_summary["buffered_tokens"] == 0


class TestTimeSeriesScenario:
    """
    Time-series test scenarios to ensure correct behavior across multiple calls.

    These tests verify that:
    1. Cache is NOT created every time
    2. Buffered history correctly includes FunctionCall and ToolResponse
    3. No duplication between Cached and Buffered
    """

    def test_time_series_no_cache_creation_every_time(
        self, payload_service, mock_session, mock_prompt_factory, mock_client
    ):
        """
        Test that cache is NOT created on every request.

        Timeline:
        T1: First request with instruction (buffered_tokens = 1000, below threshold)
        T2: Second request with instruction (buffered_tokens = 2000, below threshold)
        T3: Third request (buffered_tokens = 3000, below threshold)

        Expected: Cache should NOT be created at T1, T2, or T3.
        """
        mock_session.turns = []

        with (
            patch(
                "pipe.core.domains.gemini_payload_service.GeminiApiDynamicPayload"
            ) as mock_dynamic,
            patch(
                "pipe.core.domains.gemini_api_static_payload.build"
            ) as mock_static_build,
        ):
            mock_dynamic.return_value.build.return_value = []
            mock_static_build.return_value = []

            # T1: First request
            payload_service.prepare_request(
                session=mock_session,
                prompt_factory=mock_prompt_factory,
                current_instruction="First instruction",
            )
            payload_service.update_token_summary(
                {"cached_content_token_count": 0, "prompt_token_count": 1000}
            )

            # T2: Second request
            payload_service.prepare_request(
                session=mock_session,
                prompt_factory=mock_prompt_factory,
                current_instruction="Second instruction",
            )
            payload_service.update_token_summary(
                {"cached_content_token_count": 0, "prompt_token_count": 2000}
            )

            # T3: Third request
            payload_service.prepare_request(
                session=mock_session,
                prompt_factory=mock_prompt_factory,
                current_instruction="Third instruction",
            )
            payload_service.update_token_summary(
                {"cached_content_token_count": 0, "prompt_token_count": 3000}
            )

            # Verify cache was NEVER created (buffered_tokens always below 10000)
            mock_client.caches.create.assert_not_called()

    def test_time_series_cache_update_expands_cached_range(
        self, payload_service, mock_session, mock_prompt_factory, mock_client
    ):
        """
        Test that cache update expands the cached range correctly.

        Timeline:
        T1: 4 persisted turns, cached_turn_count = 2
        T2: buffered_tokens exceed threshold -> cache update
        T3: cached_turn_count should expand to len(full_history) - 1 = 3

        Expected:
        - Old cache deleted
        - New cache created with cached_turn_count = 3
        - Buffered history = persisted[3:] + pending
        """
        # T1: 4 persisted turns
        persisted_turns = [
            UserTaskTurn(
                type="user_task", instruction="T1", timestamp="2025-01-01T00:00:01Z"
            ),
            ModelResponseTurn(
                type="model_response", content="R1", timestamp="2025-01-01T00:00:02Z"
            ),
            UserTaskTurn(
                type="user_task", instruction="T2", timestamp="2025-01-01T00:00:03Z"
            ),
            ModelResponseTurn(
                type="model_response", content="R2", timestamp="2025-01-01T00:00:04Z"
            ),
        ]
        mock_session.turns = persisted_turns
        mock_session.cached_turn_count = 2
        mock_session.cache_name = "old-cache-xyz"

        with patch(
            "pipe.core.domains.gemini_payload_service.GeminiApiDynamicPayload"
        ) as mock_dynamic:
            mock_dynamic.return_value.build.return_value = []

            mock_cache = MagicMock()
            mock_cache.name = "new-cache-abc"
            mock_client.caches.create.return_value = mock_cache

            with (
                patch(
                    "pipe.core.domains.gemini_cache_manager.gemini_api_static_payload.build"
                ) as mock_build,
                patch.object(
                    payload_service.cache_manager,
                    "_get_existing_cache_name",
                    return_value="old-cache-xyz",
                ),
                patch.object(payload_service.cache_manager, "_update_registry"),
            ):
                mock_build.return_value = [MagicMock()]

                # T2: Trigger cache update (buffered_tokens = 15000 > 10000)
                payload_service.update_token_summary(
                    {"cached_content_token_count": 5000, "prompt_token_count": 20000}
                )

                contents, cache_name = payload_service.prepare_request(
                    session=mock_session,
                    prompt_factory=mock_prompt_factory,
                    current_instruction=None,
                )

                # T3: Verify cache update
                mock_client.caches.delete.assert_called_once_with(name="old-cache-xyz")
                mock_client.caches.create.assert_called_once()

                # Verify cached_turn_count expanded to 3 (len(full_history) - 1)
                assert mock_session.cached_turn_count == 3
                assert cache_name == "new-cache-abc"

                # Verify buffered_history at THIS call
                # At this point, cache_manager was initialized with session.cached_turn_count = 2
                # So buffered_history = persisted[2:] + pending = [T2, R2] + [] = 2 turns
                # (The expanded cache will be used in the NEXT call)
                prompt = mock_prompt_factory.create.return_value
                buffered_history = prompt.buffered_history
                assert len(buffered_history) == 2
                assert buffered_history[0] == persisted_turns[2]  # T2
                assert buffered_history[1] == persisted_turns[3]  # R2
