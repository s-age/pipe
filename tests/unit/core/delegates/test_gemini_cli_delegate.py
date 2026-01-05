"""Unit tests for gemini_cli_delegate."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.delegates import gemini_cli_delegate
from pipe.core.domains.gemini_cli_stream_processor import StreamResult
from pipe.core.models.args import TaktArgs
from pipe.core.models.turn import FunctionCallingTurn, ToolResponseTurn

from tests.factories.models.session_factory import SessionFactory


@pytest.fixture
def mock_session_service():
    """Fixture for common session service mock."""
    session_service = MagicMock()
    session_service.project_root = "/root"
    session_service.settings.api_mode = "gemini-cli"
    session_service.settings.model.name = "gemini-1.5-flash"
    session_service.current_session_id = "test-session"
    session_service.timezone_obj = MagicMock()
    return session_service


class TestReconcileToolCalls:
    """Tests for _reconcile_tool_calls function."""

    def test_reconcile_no_session_id(self):
        """Test that it returns early if session_id is None."""
        mock_session_service = MagicMock()
        mock_session_service.current_session_id = None
        stream_result = StreamResult(
            response="test", tool_calls=[], tool_results=[], stats=None
        )

        gemini_cli_delegate._reconcile_tool_calls(stream_result, mock_session_service)

        mock_session_service.get_session.assert_not_called()

    def test_reconcile_session_not_found(self, capsys):
        """Test that it prints warning if session is not found."""
        mock_session_service = MagicMock()
        mock_session_service.current_session_id = "test-session"
        mock_session_service.get_session.return_value = None
        stream_result = StreamResult(
            response="test", tool_calls=[], tool_results=[], stats=None
        )

        gemini_cli_delegate._reconcile_tool_calls(stream_result, mock_session_service)

        captured = capsys.readouterr()
        assert "Warning: Session test-session not found" in captured.err

    def test_reconcile_pools_not_empty(self, mock_session_service):
        """Test that it returns early if pools is not empty (mcp_server already ran)."""
        session = SessionFactory.create_with_turns(turn_count=1)
        # Move turn to pools
        session.pools.append(session.turns.pop(0))
        mock_session_service.get_session.return_value = session
        stream_result = StreamResult(
            response="test",
            tool_calls=[{"tool_name": "test"}],
            tool_results=[],
            stats=None,
        )

        gemini_cli_delegate._reconcile_tool_calls(stream_result, mock_session_service)

        assert len(session.pools) == 1  # Should not have added from stream

    def test_reconcile_no_tools_in_stream(self, mock_session_service):
        """Test that it returns early if no tools in stream."""
        session = SessionFactory.create()
        mock_session_service.get_session.return_value = session
        stream_result = StreamResult(
            response="test", tool_calls=[], tool_results=[], stats=None
        )

        gemini_cli_delegate._reconcile_tool_calls(stream_result, mock_session_service)

        assert len(session.pools) == 0

    @patch("pipe.core.utils.datetime.get_current_timestamp")
    def test_reconcile_success(self, mock_get_timestamp, mock_session_service):
        """Test successful reconciliation of tool calls and results."""
        mock_get_timestamp.return_value = "2025-01-01T00:00:00Z"
        session = SessionFactory.create()
        mock_session_service.get_session.return_value = session

        stream_result = StreamResult(
            response="test",
            tool_calls=[
                {"tool_name": "test_tool", "parameters": {"arg": "val"}},
            ],
            tool_results=[
                {
                    "tool_id": "test_tool-123",
                    "status": "success",
                    "output": "tool output",
                },
            ],
            stats=None,
        )

        gemini_cli_delegate._reconcile_tool_calls(stream_result, mock_session_service)

        assert len(session.pools) == 2
        assert isinstance(session.pools[0], FunctionCallingTurn)
        assert session.pools[0].response == 'test_tool({"arg": "val"})'
        assert isinstance(session.pools[1], ToolResponseTurn)
        assert session.pools[1].name == "test_tool"
        assert session.pools[1].response.status == "succeeded"
        assert session.pools[1].response.message == "tool output"
        mock_session_service.repository.save.assert_called_once_with(session)

    @patch("pipe.core.utils.datetime.get_current_timestamp")
    def test_reconcile_failure_cases(self, mock_get_timestamp, mock_session_service):
        """Test reconciliation with failed tool results (dict and str errors)."""
        mock_get_timestamp.return_value = "2025-01-01T00:00:00Z"
        session = SessionFactory.create()
        mock_session_service.get_session.return_value = session

        stream_result = StreamResult(
            response="test",
            tool_calls=[],
            tool_results=[
                {
                    "tool_id": "fail_tool_1-123",
                    "status": "failed",
                    "error": {"message": "dict error"},
                },
                {
                    "tool_id": "fail_tool_2-456",
                    "status": "failed",
                    "error": "string error",
                },
            ],
            stats=None,
        )

        gemini_cli_delegate._reconcile_tool_calls(stream_result, mock_session_service)

        assert len(session.pools) == 2
        assert session.pools[0].name == "fail_tool_1"
        assert session.pools[0].response.status == "failed"
        assert session.pools[0].response.message == "dict error"

        assert session.pools[1].name == "fail_tool_2"
        assert session.pools[1].response.status == "failed"
        assert session.pools[1].response.message == "string error"


class TestRun:
    """Tests for run function."""

    @pytest.fixture
    def mock_services(self, mock_session_service):
        """Fixture for common service mocks."""
        session_turn_service = MagicMock()
        return mock_session_service, session_turn_service

    @patch("pipe.core.delegates.gemini_cli_delegate.GeminiCliPayloadBuilder")
    @patch("pipe.core.delegates.gemini_cli_delegate.GeminiToolService")
    @patch(
        "pipe.core.delegates.gemini_cli_delegate.gemini_token_count.create_local_tokenizer"
    )
    @patch("pipe.core.delegates.gemini_cli_delegate.gemini_token_count.count_tokens")
    @patch("pipe.core.delegates.gemini_cli_delegate.call_gemini_cli")
    @patch("pipe.core.delegates.gemini_cli_delegate._reconcile_tool_calls")
    def test_run_success(
        self,
        mock_reconcile,
        mock_call_cli,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_tool_service_cls,
        mock_payload_builder_cls,
        mock_services,
    ):
        """Test successful run flow."""
        session_service, session_turn_service = mock_services
        args = TaktArgs(output_format="json")

        # Setup mocks
        mock_payload_builder = mock_payload_builder_cls.return_value
        mock_payload_builder.build.return_value = "rendered prompt"

        mock_tool_service = mock_tool_service_cls.return_value
        mock_tool_service.load_tools.return_value = []

        mock_count_tokens.return_value = 100

        stream_result = StreamResult(
            response="model response",
            tool_calls=[],
            tool_results=[],
            stats={"total": 10},
        )
        mock_call_cli.return_value = stream_result

        session = SessionFactory.create()
        session_service.get_session.return_value = session

        # Execute
        response_text, token_count, stats = gemini_cli_delegate.run(
            args, session_service, session_turn_service
        )

        # Verify
        assert response_text == "model response"
        assert token_count == 100
        assert stats == {"total": 10}

        mock_payload_builder_cls.assert_called_once_with(
            project_root="/root", api_mode="gemini-cli"
        )
        mock_payload_builder.build.assert_called_once_with(session_service)
        mock_tool_service.load_tools.assert_called_once_with("/root")
        mock_create_tokenizer.assert_called_once_with("gemini-1.5-flash")
        mock_count_tokens.assert_called_once_with(
            "rendered prompt", tools=[], tokenizer=mock_create_tokenizer.return_value
        )
        mock_call_cli.assert_called_once_with(
            session_service, "json", prompt="rendered prompt"
        )
        mock_reconcile.assert_called_once_with(stream_result, session_service)
        session_turn_service.merge_pool_into_turns.assert_called_once_with(
            "test-session"
        )

    @patch("pipe.core.delegates.gemini_cli_delegate.GeminiCliPayloadBuilder")
    @patch("pipe.core.delegates.gemini_cli_delegate.GeminiToolService")
    @patch(
        "pipe.core.delegates.gemini_cli_delegate.gemini_token_count.create_local_tokenizer"
    )
    @patch("pipe.core.delegates.gemini_cli_delegate.gemini_token_count.count_tokens")
    @patch("pipe.core.delegates.gemini_cli_delegate.call_gemini_cli")
    @patch("pipe.core.delegates.gemini_cli_delegate._reconcile_tool_calls")
    def test_run_no_session_id(
        self,
        mock_reconcile,
        mock_call_cli,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_tool_service_cls,
        mock_payload_builder_cls,
        mock_services,
    ):
        """Test run flow when no session is active."""
        session_service, session_turn_service = mock_services
        session_service.current_session_id = None
        args = TaktArgs(output_format="json")

        # Setup mocks
        mock_payload_builder = mock_payload_builder_cls.return_value
        mock_payload_builder.build.return_value = "rendered prompt"
        mock_call_cli.return_value = StreamResult(
            response="resp", tool_calls=[], tool_results=[], stats=None
        )

        # Execute
        gemini_cli_delegate.run(args, session_service, session_turn_service)

        # Verify reconciliation was skipped
        mock_reconcile.assert_not_called()
        session_turn_service.merge_pool_into_turns.assert_not_called()
