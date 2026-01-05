"""Unit tests for GeminiApiAgent."""

import os
import zoneinfo
from unittest.mock import MagicMock, patch

import pytest
from google.genai import types
from pipe.core.agents.gemini_api import GeminiApiAgent
from pipe.core.models.args import TaktArgs
from pipe.core.models.unified_chunk import TextChunk

from tests.factories.models.session_factory import SessionFactory
from tests.factories.models.settings_factory import create_test_settings


@pytest.fixture
def mock_session_service():
    """Create a mock SessionService."""
    service = MagicMock()
    service.settings = create_test_settings()
    service.project_root = "/mock/project"
    service.current_session = SessionFactory.create()
    return service


@pytest.fixture
def agent(mock_session_service):
    """Create a GeminiApiAgent instance with mocked dependencies."""
    with (
        patch("pipe.core.agents.gemini_api.genai.Client"),
        patch("pipe.core.agents.gemini_api.PromptFactory"),
        patch("pipe.core.agents.gemini_api.ResourceRepository"),
        patch("pipe.core.agents.gemini_api.gemini_token_count.create_local_tokenizer"),
    ):
        return GeminiApiAgent(mock_session_service)


class TestGeminiApiAgentInit:
    """Tests for GeminiApiAgent.__init__."""

    def test_init_success(self, mock_session_service):
        """Test successful initialization of GeminiApiAgent."""
        with (
            patch("pipe.core.agents.gemini_api.genai.Client") as mock_client_cls,
            patch(
                "pipe.core.agents.gemini_api.PromptFactory"
            ) as mock_prompt_factory_cls,
            patch(
                "pipe.core.agents.gemini_api.ResourceRepository"
            ) as mock_resource_repo_cls,
            patch(
                "pipe.core.agents.gemini_api.gemini_token_count.create_local_tokenizer"
            ) as mock_create_tokenizer,
        ):
            agent = GeminiApiAgent(mock_session_service)

            assert agent.session_service == mock_session_service
            assert agent.settings == mock_session_service.settings
            assert agent.project_root == mock_session_service.project_root
            assert agent.tool_service is not None
            assert agent.payload_service is not None
            assert agent.prompt_factory is not None

            mock_client_cls.assert_called_once()
            mock_prompt_factory_cls.assert_called_once_with(
                project_root=mock_session_service.project_root,
                resource_repository=mock_resource_repo_cls.return_value,
            )
            mock_create_tokenizer.assert_called_once_with(
                mock_session_service.settings.model.name
            )

    def test_init_with_custom_tool_service(self, mock_session_service):
        """Test initialization with a custom tool service."""
        mock_tool_service = MagicMock()
        with (
            patch("pipe.core.agents.gemini_api.genai.Client"),
            patch("pipe.core.agents.gemini_api.PromptFactory"),
            patch("pipe.core.agents.gemini_api.ResourceRepository"),
            patch(
                "pipe.core.agents.gemini_api.gemini_token_count.create_local_tokenizer"
            ),
        ):
            agent = GeminiApiAgent(mock_session_service, tool_service=mock_tool_service)
            assert agent.tool_service == mock_tool_service

    def test_init_timezone_fallback(self, mock_session_service):
        """Test timezone fallback to UTC when ZoneInfoNotFoundError occurs."""
        mock_session_service.settings.timezone = "Invalid/Timezone"
        with (
            patch("pipe.core.agents.gemini_api.genai.Client"),
            patch("pipe.core.agents.gemini_api.PromptFactory"),
            patch("pipe.core.agents.gemini_api.ResourceRepository"),
            patch(
                "pipe.core.agents.gemini_api.gemini_token_count.create_local_tokenizer"
            ),
            patch("pipe.core.agents.gemini_api.zoneinfo.ZoneInfo") as mock_zi,
        ):
            # First call raises, second call (fallback) succeeds
            mock_zi.side_effect = [zoneinfo.ZoneInfoNotFoundError, MagicMock()]

            agent = GeminiApiAgent(mock_session_service)

            # Verify it tried the invalid one and then UTC
            mock_zi.assert_any_call("Invalid/Timezone")
            mock_zi.assert_any_call("UTC")
            assert agent.timezone is not None


class TestGeminiApiAgentRun:
    """Tests for GeminiApiAgent.run."""

    @patch("pipe.core.services.session_turn_service.SessionTurnService")
    @patch("pipe.core.delegates.gemini_api_delegate.run_stream")
    def test_run_delegation(
        self, mock_run_stream, mock_turn_service_cls, agent, mock_session_service
    ):
        """Test that run() delegates to gemini_api_delegate.run_stream."""
        args = TaktArgs(instruction="test")
        mock_run_stream.return_value = [("chunk", "final response", 100, [], "thought")]

        response, token_count, turns, thought = agent.run(args, mock_session_service)

        assert response == "final response"
        assert token_count == 100
        assert turns == []
        assert thought == "thought"
        mock_run_stream.assert_called_once()


class TestGeminiApiAgentRunStream:
    """Tests for GeminiApiAgent.run_stream."""

    @patch("pipe.core.services.session_turn_service.SessionTurnService")
    @patch("pipe.core.delegates.gemini_api_delegate.run_stream")
    def test_run_stream_delegation(
        self, mock_run_stream, mock_turn_service_cls, agent, mock_session_service
    ):
        """Test that run_stream() yields from gemini_api_delegate.run_stream."""
        args = TaktArgs(instruction="test")
        mock_run_stream.return_value = iter([("chunk", None, None, [], None)])

        results = list(agent.run_stream(args, mock_session_service))

        assert len(results) == 1
        assert results[0][0] == "chunk"
        mock_run_stream.assert_called_once()


class TestGeminiApiAgentStreamContent:
    """Tests for GeminiApiAgent.stream_content."""

    def test_stream_content_flow(self, agent, mock_session_service):
        """Test the full flow of stream_content."""
        mock_session_service.current_session.session_id = "test-session"

        with (
            patch.object(
                agent.tool_service, "load_tools", return_value=[]
            ) as mock_load_tools,
            patch.object(
                agent.tool_service, "convert_to_genai_tools", return_value=[]
            ) as mock_convert_tools,
            patch.object(
                agent.payload_service, "prepare_request", return_value=([], "cache-123")
            ) as mock_prepare,
            patch.object(agent, "_log_cache_decision") as mock_log_cache,
            patch.object(agent, "_build_generation_config") as mock_build_config,
            patch("pipe.core.agents.gemini_api.genai.Client"),
            patch.object(
                agent,
                "_execute_streaming_call",
                return_value=iter([TextChunk(content="hello")]),
            ) as mock_execute,
        ):
            results = list(agent.stream_content())

            assert os.environ["PIPE_SESSION_ID"] == "test-session"
            mock_load_tools.assert_called_once_with(agent.project_root)
            mock_convert_tools.assert_called_once()
            mock_prepare.assert_called_once()
            mock_log_cache.assert_called_once()
            mock_build_config.assert_called_once()
            mock_execute.assert_called_once()
            assert len(results) == 1
            assert results[0].content == "hello"


class TestGeminiApiAgentLogCacheDecision:
    """Tests for GeminiApiAgent._log_cache_decision."""

    @patch("pipe.core.agents.gemini_api.StreamingLogRepository")
    @patch("pipe.core.agents.gemini_api.get_current_datetime")
    def test_log_cache_decision_creating_cache(
        self, mock_get_now, mock_log_repo_cls, agent
    ):
        """Test logging when creating/updating cache."""
        session_data = SessionFactory.create(cached_turn_count=5)
        session_data.turns = MagicMock()
        session_data.turns.__len__.return_value = 10
        session_data.cached_content_token_count = 1000
        session_data.token_count = 2000

        mock_repo = mock_log_repo_cls.return_value
        agent.settings.model.cache_update_threshold = 500

        agent._log_cache_decision(session_data, "cache-123", 600)

        mock_repo.open.assert_called_once_with(mode="a")
        mock_repo.write_log_line.assert_called_once()
        args = mock_repo.write_log_line.call_args[0]
        assert args[0] == "CACHE_DECISION"
        assert "CREATING/UPDATING cache" in args[1]
        assert "key=cache-123" in args[1]
        mock_repo.close.assert_called_once()

    @patch("pipe.core.agents.gemini_api.StreamingLogRepository")
    @patch("pipe.core.agents.gemini_api.get_current_datetime")
    def test_log_cache_decision_using_existing_cache(
        self, mock_get_now, mock_log_repo_cls, agent
    ):
        """Test logging when using existing cache."""
        session_data = SessionFactory.create(cached_turn_count=5)
        session_data.turns = MagicMock()
        session_data.turns.__len__.return_value = 10

        mock_repo = mock_log_repo_cls.return_value
        agent.settings.model.cache_update_threshold = 1000

        agent._log_cache_decision(session_data, "cache-123", 500)

        args = mock_repo.write_log_line.call_args[0]
        assert "USING EXISTING cache" in args[1]

    @patch("pipe.core.agents.gemini_api.StreamingLogRepository")
    @patch("pipe.core.agents.gemini_api.get_current_datetime")
    def test_log_cache_decision_no_cache_below_threshold(
        self, mock_get_now, mock_log_repo_cls, agent
    ):
        """Test logging when no cache is used (below threshold)."""
        session_data = SessionFactory.create(cached_turn_count=0)
        session_data.turns = MagicMock()
        session_data.turns.__len__.return_value = 5
        session_data.cached_content_token_count = 0

        mock_repo = mock_log_repo_cls.return_value
        agent.settings.model.cache_update_threshold = 1000

        agent._log_cache_decision(session_data, None, 500)

        args = mock_repo.write_log_line.call_args[0]
        assert "NO CACHE (below threshold)" in args[1]

    @patch("pipe.core.agents.gemini_api.StreamingLogRepository")
    @patch("pipe.core.agents.gemini_api.get_current_datetime")
    def test_log_cache_decision_no_cache_empty_static(
        self, mock_get_now, mock_log_repo_cls, agent
    ):
        """Test logging when no cache is used (empty static content)."""
        session_data = SessionFactory.create(cached_turn_count=0)
        session_data.turns = MagicMock()
        session_data.turns.__len__.return_value = 5
        session_data.cached_content_token_count = 100  # Non-zero but no cache_name

        mock_repo = mock_log_repo_cls.return_value

        agent._log_cache_decision(session_data, None, 500)

        args = mock_repo.write_log_line.call_args[0]
        assert "NO CACHE (static.cached_content is empty)" in args[1]


class TestGeminiApiAgentBuildGenerationConfig:
    """Tests for GeminiApiAgent._build_generation_config."""

    def test_build_generation_config_defaults(self, agent):
        """Test building config with default settings."""
        session_data = SessionFactory.create(hyperparameters=None)
        tools = [MagicMock(spec=types.Tool)]

        config = agent._build_generation_config(session_data, None, tools)

        assert config.temperature == agent.settings.parameters.temperature.value
        assert config.top_p == agent.settings.parameters.top_p.value
        assert config.top_k == agent.settings.parameters.top_k.value
        assert config.tools == tools
        assert config.cached_content is None

    def test_build_generation_config_overrides(self, agent):
        """Test building config with session hyperparameter overrides."""
        from pipe.core.models.hyperparameters import Hyperparameters

        session_data = SessionFactory.create(
            hyperparameters=Hyperparameters(temperature=0.9, top_p=0.8, top_k=50)
        )

        config = agent._build_generation_config(session_data, "cache-123", [])

        assert config.temperature == 0.9
        assert config.top_p == 0.8
        assert config.top_k == 50
        assert config.cached_content == "cache-123"
        assert config.tools is None  # Tools should be None when using cache


class TestGeminiApiAgentExecuteStreamingCall:
    """Tests for GeminiApiAgent._execute_streaming_call."""

    @patch("pipe.core.agents.gemini_api.StreamingLogRepository")
    @patch("pipe.core.agents.gemini_api.GeminiApiStreamProcessor")
    def test_execute_streaming_call_success(
        self, mock_processor_cls, mock_log_repo_cls, agent
    ):
        """Test successful execution of streaming call."""
        mock_client = MagicMock()
        mock_stream = MagicMock()
        mock_client.models.generate_content_stream.return_value = mock_stream

        mock_processor = mock_processor_cls.return_value
        mock_processor.process_stream.return_value = iter([TextChunk(content="chunk")])
        mock_processor.get_last_raw_response.return_value = "raw response"

        session_data = SessionFactory.create()
        config = MagicMock(spec=types.GenerateContentConfig)

        results = list(
            agent._execute_streaming_call(mock_client, "prompt", config, session_data)
        )

        assert len(results) == 1
        assert results[0].content == "chunk"
        assert agent.last_raw_response == "raw response"
        assert agent.last_stream_processor == mock_processor

        mock_client.models.generate_content_stream.assert_called_once_with(
            contents="prompt", config=config, model=agent.model_name
        )
        mock_processor.process_stream.assert_called_once_with(mock_stream)

    @patch("pipe.core.agents.gemini_api.StreamingLogRepository")
    def test_execute_streaming_call_error(self, mock_log_repo_cls, agent):
        """Test error handling during streaming call."""
        mock_client = MagicMock()
        mock_client.models.generate_content_stream.side_effect = Exception("API Error")

        session_data = SessionFactory.create()
        config = MagicMock(spec=types.GenerateContentConfig)

        with pytest.raises(
            RuntimeError, match="Error during Gemini API execution: API Error"
        ):
            list(
                agent._execute_streaming_call(
                    mock_client, "prompt", config, session_data
                )
            )
