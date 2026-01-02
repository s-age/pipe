"""
Unit tests for GeminiApiPayload orchestrator.
"""

from unittest.mock import MagicMock, patch

import pytest
from google.genai import types
from pipe.core.domains.gemini_api_payload import GeminiApiPayload
from pipe.core.domains.gemini_cache_manager import TokenCountSummary
from pipe.core.models.session import Session
from pipe.core.models.settings import Settings


@pytest.fixture
def mock_client():
    """Mock Gemini API client."""
    return MagicMock()


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    settings = MagicMock(spec=Settings)
    settings.model = MagicMock()
    settings.model.name = "gemini-1.5-flash"
    settings.model.cache_update_threshold = 1000
    return settings


@pytest.fixture
def mock_session():
    """Mock session object."""
    session = MagicMock(spec=Session)
    session.turns = []
    session.artifacts = []
    session.cached_turn_count = 0
    return session


@pytest.fixture
def mock_prompt_factory():
    """Mock prompt factory."""
    factory = MagicMock()
    factory.create.return_value = MagicMock()
    return factory


@pytest.fixture
def payload_instance(mock_client, mock_settings):
    """Create a GeminiApiPayload instance with mocked dependencies."""
    with patch("pipe.core.domains.gemini_api_payload.GeminiCacheManager"):
        return GeminiApiPayload(
            client=mock_client,
            project_root="/mock/root",
            settings=mock_settings,
        )


class TestGeminiApiPayloadInit:
    """Tests for GeminiApiPayload.__init__."""

    @patch("pipe.core.domains.gemini_api_payload.GeminiCacheManager")
    def test_init_success(self, MockCacheManager, mock_client, mock_settings):
        """Test successful initialization."""
        payload = GeminiApiPayload(
            client=mock_client,
            project_root="/mock/root",
            settings=mock_settings,
        )

        assert payload.client == mock_client
        assert payload.project_root == "/mock/root"
        assert payload.settings == mock_settings
        assert payload.last_token_summary == {
            "cached_tokens": 0,
            "current_prompt_tokens": 0,
            "buffered_tokens": 0,
        }
        assert payload.last_dynamic_tokens == 0

        # Verify GeminiCacheManager was instantiated correctly
        MockCacheManager.assert_called_once_with(
            client=mock_client,
            project_root="/mock/root",
            model_name=mock_settings.model.name,
            cache_update_threshold=mock_settings.model.cache_update_threshold,
            prompt_factory=None,
            settings=mock_settings,
        )

    def test_init_invalid_settings(self, mock_client, mock_settings):
        """Test initialization with invalid settings (missing model.name)."""
        del mock_settings.model.name
        with pytest.raises(
            ValueError, match="settings.model must be a ModelConfig object"
        ):
            GeminiApiPayload(
                client=mock_client,
                project_root="/mock/root",
                settings=mock_settings,
            )


class TestGeminiApiPayloadPrepareRequest:
    """Tests for GeminiApiPayload.prepare_request."""

    @patch("pipe.core.domains.gemini_api_payload.GeminiApiDynamicPayload")
    @patch("pipe.core.domains.gemini_api_static_payload.build")
    @patch("pipe.core.domains.gemini_token_count.create_local_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.count_tokens")
    def test_prepare_request_no_cache(
        self,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_static_build,
        MockDynamicPayload,
        payload_instance,
        mock_session,
        mock_prompt_factory,
    ):
        """Test prepare_request when no cache is used."""
        # Setup mocks
        payload_instance.cache_manager.update_if_needed.return_value = (
            None,  # cache_name
            0,  # confirmed_cached_count
            [],  # buffered_history
        )

        mock_static_build.return_value = [MagicMock(spec=types.Content)]

        mock_dynamic_builder = MockDynamicPayload.return_value
        mock_dynamic_builder.render_dynamic_json.return_value = "{}"
        mock_dynamic_builder.build.return_value = [MagicMock(spec=types.Content)]

        mock_count_tokens.return_value = 50

        # Execute
        contents, cache_name = payload_instance.prepare_request(
            session=mock_session,
            prompt_factory=mock_prompt_factory,
            current_instruction="test instruction",
        )

        # Verify
        assert cache_name is None
        assert len(contents) == 2  # Static + Dynamic
        assert mock_session.cached_turn_count == 0
        assert payload_instance.last_dynamic_tokens == 50

        # Verify static build was called
        mock_static_build.assert_called_once()

        # Verify dynamic builder was used
        mock_dynamic_builder.render_dynamic_json.assert_called_once()
        mock_dynamic_builder.build.assert_called_once()

    @patch("pipe.core.domains.gemini_api_payload.GeminiApiDynamicPayload")
    @patch("pipe.core.domains.gemini_api_static_payload.build")
    @patch("pipe.core.domains.gemini_token_count.create_local_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.count_tokens")
    def test_prepare_request_with_cache(
        self,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_static_build,
        MockDynamicPayload,
        payload_instance,
        mock_session,
        mock_prompt_factory,
    ):
        """Test prepare_request when cache is used."""
        # Setup mocks
        payload_instance.cache_manager.update_if_needed.return_value = (
            "cached-content-123",  # cache_name
            5,  # confirmed_cached_count
            [],  # buffered_history
        )

        mock_dynamic_builder = MockDynamicPayload.return_value
        mock_dynamic_builder.render_dynamic_json.return_value = "{}"
        mock_dynamic_builder.build.return_value = [MagicMock(spec=types.Content)]

        mock_count_tokens.return_value = 30

        # Execute
        contents, cache_name = payload_instance.prepare_request(
            session=mock_session,
            prompt_factory=mock_prompt_factory,
        )

        # Verify
        assert cache_name == "cached-content-123"
        assert len(contents) == 1  # Only dynamic
        assert mock_session.cached_turn_count == 5
        assert payload_instance.last_dynamic_tokens == 30

        # Verify static build was NOT called
        mock_static_build.assert_not_called()


class TestGeminiApiPayloadUpdateTokenSummary:
    """Tests for GeminiApiPayload.update_token_summary."""

    def test_update_token_summary_basic(self, payload_instance):
        """Test basic token summary update with dynamic token subtraction."""
        payload_instance.last_dynamic_tokens = 100

        usage_metadata = {
            "cached_content_token_count": 500,
            "prompt_token_count": 800,
        }

        payload_instance.update_token_summary(usage_metadata)

        # buffered = (800 - 500) - 100 = 200
        assert payload_instance.last_token_summary == TokenCountSummary(
            cached_tokens=500,
            current_prompt_tokens=800,
            buffered_tokens=200,
        )

    def test_update_token_summary_negative_buffered_clamped(self, payload_instance):
        """Test that buffered_tokens is clamped to 0 if subtraction results in negative."""
        payload_instance.last_dynamic_tokens = 500

        usage_metadata = {
            "cached_content_token_count": 500,
            "prompt_token_count": 800,
        }

        payload_instance.update_token_summary(usage_metadata)

        # raw_buffered = 800 - 500 = 300
        # adjusted = 300 - 500 = -200 -> clamped to 0
        assert payload_instance.last_token_summary["buffered_tokens"] == 0

    def test_update_token_summary_missing_metadata(self, payload_instance):
        """Test update with missing metadata fields (defaults to 0)."""
        payload_instance.last_dynamic_tokens = 0

        payload_instance.update_token_summary({})

        assert payload_instance.last_token_summary == TokenCountSummary(
            cached_tokens=0,
            current_prompt_tokens=0,
            buffered_tokens=0,
        )
