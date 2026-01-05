"""Unit tests for gemini_api_delegate."""

import zoneinfo
from unittest.mock import MagicMock, patch

import pytest
from pipe.core.delegates import gemini_api_delegate
from pipe.core.models.turn import FunctionCallingTurn, ModelResponseTurn
from pipe.core.models.unified_chunk import (
    MetadataChunk,
    TextChunk,
    ToolCallChunk,
    UsageMetadata,
)


@pytest.fixture
def session_service():
    """Create a mock SessionService."""
    service = MagicMock()
    service.settings.max_tool_calls = 5
    service.current_session.session_id = "test-session-123"
    service.current_session.cached_content_token_count = 0
    service.current_session.token_count = 0
    service.current_session.turns = []
    service.current_session.cumulative_total_tokens = 1000
    service.current_session.cumulative_cached_tokens = 500
    service.current_session_id = "test-session-123"
    service.timezone_obj = zoneinfo.ZoneInfo("UTC")
    service.project_root = "/mock/project"
    service.repository = MagicMock()
    service.get_session.return_value = service.current_session
    return service


@pytest.fixture
def session_turn_service():
    """Create a mock SessionTurnService."""
    return MagicMock()


@pytest.fixture
def takt_args():
    """Create mock TaktArgs."""
    args = MagicMock()
    args.session = "test-session-123"
    return args


class TestGeminiApiDelegate:
    """Tests for gemini_api_delegate functions."""

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_text_only(
        self,
        mock_get_timestamp,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream with a simple text response."""
        # Setup mocks
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-response-data"
        mock_agent.last_cached_turn_count = 3
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        # Mock stream content
        mock_agent.stream_content.return_value = iter(
            [
                TextChunk(content="Hello", is_thought=False),
                TextChunk(content=" world", is_thought=False),
                MetadataChunk(
                    usage=UsageMetadata(
                        prompt_token_count=10,
                        candidates_token_count=5,
                        total_token_count=15,
                        cached_content_token_count=5,
                    )
                ),
            ]
        )

        # Execute
        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        # Verify yields
        assert "Hello" in results
        assert " world" in results

        # Verify final result
        final_result = results[-1]
        assert final_result[0] == "end"
        assert final_result[1] == "Hello world"
        # token_count = raw_total - cache_delta = 15 - (5 - 0) = 10
        assert final_result[2] == 10
        assert isinstance(final_result[3][0], ModelResponseTurn)
        assert final_result[4] == ""

        # Verify service calls
        session_turn_service.merge_pool_into_turns.assert_called()
        mock_agent.payload_service.update_token_summary.assert_called()

        # Verify meta service calls at the end
        mock_meta_service = mock_meta_service_cls.return_value
        mock_meta_service.update_token_count.assert_called()
        mock_meta_service.update_cached_content_token_count.assert_called_with(
            "test-session-123", 5
        )
        mock_meta_service.update_cached_turn_count.assert_called_with(
            "test-session-123", 3
        )

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.execute_tool")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_with_tool_call(
        self,
        mock_get_timestamp,
        mock_execute_tool,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream with a tool call followed by text."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 2
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        # First iteration: Tool call
        stream1 = iter(
            [
                ToolCallChunk(name="test_tool", args={"arg1": "val1"}),
                MetadataChunk(
                    usage=UsageMetadata(
                        prompt_token_count=20,
                        candidates_token_count=10,
                        total_token_count=30,
                        cached_content_token_count=0,
                    )
                ),
            ]
        )

        # Second iteration: Final text
        stream2 = iter(
            [
                TextChunk(content="Tool result processed", is_thought=False),
                MetadataChunk(
                    usage=UsageMetadata(
                        prompt_token_count=50,
                        candidates_token_count=5,
                        total_token_count=55,
                        cached_content_token_count=0,
                    )
                ),
            ]
        )

        mock_agent.stream_content.side_effect = [stream1, stream2]
        mock_execute_tool.return_value = {"message": "Success"}

        # Mock repository.find to cover raw_response update in pool
        mock_session = MagicMock()
        mock_session.pools = [
            FunctionCallingTurn(
                type="function_calling", response="test_tool()", timestamp="now"
            )
        ]
        session_service.repository.find.return_value = mock_session

        # Execute
        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        # Verify tool call markdown was yielded
        assert any("Tool call: test_tool" in str(r) for r in results)
        assert any("Tool status: succeeded" in str(r) for r in results)
        assert "Tool result processed" in results

        # Verify tool execution
        mock_execute_tool.assert_called_once_with("test_tool", {"arg1": "val1"})

        # Verify raw_response update
        assert mock_session.pools[0].raw_response == "raw-data"
        session_service.repository.save.assert_called()

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_empty_stream(
        self,
        mock_get_timestamp,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream with an empty stream from agent."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.stream_content.return_value = iter([])
        mock_agent.last_raw_response = "empty"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert "API Error: Model stream was empty." in results
        final_result = results[-1]
        assert final_result[1] == "API Error: Model stream was empty."

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.execute_tool")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_max_tool_calls(
        self,
        mock_get_timestamp,
        mock_execute_tool,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream stops after max tool calls."""
        session_service.settings.max_tool_calls = 1
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        # Agent keeps returning tool calls
        mock_agent.stream_content.return_value = iter(
            [
                ToolCallChunk(name="loop_tool", args={}),
                MetadataChunk(
                    usage=UsageMetadata(prompt_token_count=10, total_token_count=10)
                ),
            ]
        )
        mock_execute_tool.return_value = "OK"

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert (
            "Error: Maximum number of tool calls reached. Halting execution." in results
        )

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_with_thoughts(
        self,
        mock_get_timestamp,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream with thought chunks."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        mock_agent.stream_content.return_value = iter(
            [
                TextChunk(content="Thinking...", is_thought=True),
                TextChunk(content="Final answer", is_thought=False),
                MetadataChunk(
                    usage=UsageMetadata(prompt_token_count=10, total_token_count=20)
                ),
            ]
        )

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert "Thinking..." in results
        assert "Final answer" in results
        final_result = results[-1]
        assert final_result[4] == "Thinking..."
        assert final_result[1] == "Final answer"

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_thought_only(
        self,
        mock_get_timestamp,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream when model returns only thoughts (covers line 138)."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        mock_agent.stream_content.return_value = iter(
            [
                TextChunk(content="Thinking...", is_thought=True),
                MetadataChunk(
                    usage=UsageMetadata(prompt_token_count=10, total_token_count=20)
                ),
            ]
        )

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert any(
            "(Model generated thoughts only. Check logs for details.)" in str(r)
            for r in results
        )

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_usage_only_no_content(
        self,
        mock_get_timestamp,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream when model returns usage but no content (refusal)."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        mock_agent.stream_content.return_value = iter(
            [
                MetadataChunk(
                    usage=UsageMetadata(prompt_token_count=100, total_token_count=100)
                ),
            ]
        )

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert any(
            "Model consumed tokens but generated no output" in str(r) for r in results
        )

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.execute_tool")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_tool_error(
        self,
        mock_get_timestamp,
        mock_execute_tool,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream when tool execution raises an exception."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        mock_agent.stream_content.side_effect = [
            iter(
                [
                    ToolCallChunk(name="fail_tool", args={}),
                    MetadataChunk(
                        usage=UsageMetadata(prompt_token_count=10, total_token_count=10)
                    ),
                ]
            ),
            iter(
                [
                    TextChunk(content="Recovered", is_thought=False),
                    MetadataChunk(
                        usage=UsageMetadata(prompt_token_count=10, total_token_count=10)
                    ),
                ]
            ),
        ]
        mock_execute_tool.side_effect = Exception("Tool crashed")

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert any("Tool status: failed" in str(r) for r in results)
        assert "Recovered" in results

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.execute_tool")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_tool_result_formats(
        self,
        mock_get_timestamp,
        mock_execute_tool,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream with different tool result formats (covers 258-261)."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        # Case: tool_result is a dict with 'content' but no 'message'
        mock_agent.stream_content.side_effect = [
            iter(
                [
                    ToolCallChunk(name="format_tool", args={}),
                    MetadataChunk(
                        usage=UsageMetadata(prompt_token_count=10, total_token_count=10)
                    ),
                ]
            ),
            iter(
                [
                    TextChunk(content="Done", is_thought=False),
                    MetadataChunk(
                        usage=UsageMetadata(prompt_token_count=10, total_token_count=10)
                    ),
                ]
            ),
        ]
        mock_execute_tool.return_value = {"content": "Result in content"}

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert any("Tool status: succeeded" in str(r) for r in results)
        assert "Done" in results

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.execute_tool")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_tool_result_non_dict(
        self,
        mock_get_timestamp,
        mock_execute_tool,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream when tool result is not a dict (covers line 231 and 265)."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        mock_agent.stream_content.side_effect = [
            iter(
                [
                    ToolCallChunk(name="string_tool", args={}),
                    MetadataChunk(
                        usage=UsageMetadata(prompt_token_count=10, total_token_count=10)
                    ),
                ]
            ),
            iter(
                [
                    TextChunk(content="Done", is_thought=False),
                    MetadataChunk(
                        usage=UsageMetadata(prompt_token_count=10, total_token_count=10)
                    ),
                ]
            ),
        ]
        mock_execute_tool.return_value = "Success string"

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert any("Tool status: succeeded" in str(r) for r in results)
        assert "Done" in results

    @patch("pipe.core.delegates.gemini_api_delegate.GeminiApiAgent")
    @patch("pipe.core.delegates.gemini_api_delegate.StreamingLogRepository")
    @patch("pipe.core.services.session_meta_service.SessionMetaService")
    @patch("pipe.core.delegates.gemini_api_delegate.get_current_timestamp")
    def test_run_stream_usage_no_cached_count(
        self,
        mock_get_timestamp,
        mock_meta_service_cls,
        mock_log_repo_cls,
        mock_agent_cls,
        session_service,
        session_turn_service,
        takt_args,
    ):
        """Test run_stream when usage metadata has no cached count (covers line 181)."""
        mock_agent = mock_agent_cls.return_value
        mock_agent.last_raw_response = "raw-data"
        mock_agent.last_cached_turn_count = 0
        mock_get_timestamp.return_value = "2026-01-01T12:00:00Z"

        mock_agent.stream_content.return_value = iter(
            [
                TextChunk(content="Done", is_thought=False),
                MetadataChunk(
                    usage=UsageMetadata(
                        prompt_token_count=10,
                        candidates_token_count=5,
                        total_token_count=15,
                        cached_content_token_count=None,
                    )
                ),
            ]
        )

        results = list(
            gemini_api_delegate.run_stream(
                takt_args, session_service, session_turn_service
            )
        )

        assert "Done" in results
        # Verify update_cached_content_token_count was called with 0
        mock_meta_service = mock_meta_service_cls.return_value
        mock_meta_service.update_cached_content_token_count.assert_called_with(
            "test-session-123", 0
        )
