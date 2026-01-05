"""Unit tests for GeminiCliAgent and call_gemini_cli."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.agents.gemini_cli import GeminiCliAgent, call_gemini_cli
from pipe.core.models.args import TaktArgs
from pipe.core.models.turn import ModelResponseTurn

from tests.factories.models import SessionFactory


@pytest.fixture
def mock_session_service():
    """Create a mock SessionService."""
    service = MagicMock()
    service.project_root = "/mock/project"
    service.current_session_id = "test-session-123"
    service.settings.model.name = "gemini-1.5-flash"
    service.settings.api_mode = "gemini-cli"
    service.settings.timezone = "UTC"
    service.settings.language = "japanese"
    service.settings.parameters.temperature.value = 0.7
    service.settings.parameters.top_p = MagicMock()
    service.settings.parameters.top_p.value = 0.5
    service.settings.parameters.top_k = MagicMock()
    service.settings.parameters.top_k.value = 5
    service.timezone_obj = MagicMock()
    return service


@pytest.fixture
def mock_session_turn_service():
    """Create a mock SessionTurnService."""
    # Patch the source module because it's imported inside functions
    with patch("pipe.core.services.session_turn_service.SessionTurnService") as mock:
        yield mock.return_value


@pytest.fixture
def mock_timestamp():
    """Mock get_current_timestamp to return a fixed string."""
    with patch("pipe.core.utils.datetime.get_current_timestamp") as mock:
        mock.return_value = "2025-01-01T00:00:00Z"
        yield mock


class TestCallGeminiCli:
    """Tests for call_gemini_cli function."""

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    @patch("pipe.core.repositories.streaming_log_repository.StreamingLogRepository")
    def test_call_gemini_cli_json_success(
        self,
        mock_log_repo,
        mock_builder_cls,
        mock_popen,
        mock_session_service,
    ):
        """Test successful call to gemini-cli with json output."""
        # Setup mocks
        mock_builder = mock_builder_cls.return_value
        mock_builder.build.return_value = '{"prompt": "test"}'

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout.readline.side_effect = [
            '{"response": "Hello", "stats": {"total_tokens": 10}}',
            "",
        ]
        mock_process.stderr.read.return_value = "no error"
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Execute
        result = call_gemini_cli(mock_session_service, output_format="json")

        # Verify
        assert result == {"response": "Hello", "stats": {"total_tokens": 10}}
        mock_popen.assert_called_once()
        command = mock_popen.call_args[0][0]
        assert "gemini" in command
        assert "-o" in command
        assert "json" in command

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    @patch("pipe.core.domains.gemini_cli_stream_processor.GeminiCliStreamProcessor")
    def test_call_gemini_cli_stream_json_success(
        self,
        mock_processor_cls,
        mock_builder_cls,
        mock_popen,
        mock_session_service,
    ):
        """Test successful call to gemini-cli with stream-json output."""
        # Setup mocks
        mock_builder = mock_builder_cls.return_value
        mock_builder.build.return_value = '{"prompt": "test"}'

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ['{"type": "message"}', ""]
        mock_process.stderr.read.return_value = ""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        mock_processor = mock_processor_cls.return_value
        mock_processor.get_result.return_value = MagicMock()

        # Execute
        result = call_gemini_cli(mock_session_service, output_format="stream-json")

        # Verify
        assert result == mock_processor.get_result.return_value
        mock_processor.process_line.assert_called_with('{"type": "message"}')

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_call_gemini_cli_text_success(
        self, mock_builder_cls, mock_popen, mock_session_service
    ):
        """Test successful call to gemini-cli with text output."""
        # Setup mocks
        mock_builder = mock_builder_cls.return_value
        mock_builder.build.return_value = '{"prompt": "test"}'

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["Hello world", ""]
        mock_process.stderr.read.return_value = ""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Execute
        result = call_gemini_cli(mock_session_service, output_format="text")

        # Verify
        assert result == {"response": "Hello world", "stats": None}

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    def test_call_gemini_cli_with_provided_prompt(
        self, mock_popen, mock_session_service
    ):
        """Test call_gemini_cli with provided prompt string."""
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["{}", ""]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        call_gemini_cli(mock_session_service, prompt="Custom prompt")

        mock_process.stdin.write.assert_called_once_with("Custom prompt")

    def test_call_gemini_cli_missing_model_name(self, mock_session_service):
        """Test ValueError when model name is missing."""
        mock_session_service.settings.model.name = None
        with pytest.raises(ValueError, match="'model' not found in settings"):
            call_gemini_cli(mock_session_service)

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_call_gemini_cli_command_not_found(
        self, mock_builder_cls, mock_popen, mock_session_service
    ):
        """Test error when gemini command is not found."""
        mock_popen.side_effect = FileNotFoundError()

        with pytest.raises(RuntimeError, match="gemini' command not found"):
            call_gemini_cli(mock_session_service)

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_call_gemini_cli_execution_error(
        self, mock_builder_cls, mock_popen, mock_session_service
    ):
        """Test error when gemini-cli returns non-zero exit code."""
        mock_process = MagicMock()
        mock_process.stdout.readline.return_value = ""
        mock_process.wait.return_value = 1
        mock_process.stderr.read.return_value = "Some error"
        mock_popen.return_value = mock_process

        with pytest.raises(RuntimeError, match="Error during gemini-cli execution"):
            call_gemini_cli(mock_session_service)

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_call_gemini_cli_stream_json_execution_error(
        self, mock_builder_cls, mock_popen, mock_session_service
    ):
        """Test RuntimeError when gemini-cli returns non-zero code in stream-json mode (line 131)."""
        mock_process = MagicMock()
        mock_process.stdout.readline.return_value = ""
        mock_process.stderr.read.return_value = "Stream error"
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process

        with pytest.raises(
            RuntimeError, match="Error during gemini-cli execution: Stream error"
        ):
            call_gemini_cli(mock_session_service, output_format="stream-json")

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_call_gemini_cli_no_stdout(
        self, mock_builder_cls, mock_popen, mock_session_service
    ):
        """Test call_gemini_cli when stdout is None (covers lines 120, 131)."""
        mock_process = MagicMock()
        mock_process.stdout = None
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Test for stream-json
        call_gemini_cli(mock_session_service, output_format="stream-json")

        # Test for json
        call_gemini_cli(mock_session_service, output_format="json")

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_call_gemini_cli_unexpected_error_reraise(
        self, mock_builder_cls, mock_popen, mock_session_service
    ):
        """Test reraising error when 'gemini' and 'not found' are in exception (line 163)."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.stdout.readline.side_effect = Exception("gemini command not found")

        with pytest.raises(Exception, match="gemini command not found"):
            call_gemini_cli(mock_session_service)

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_call_gemini_cli_unexpected_error_generic(
        self, mock_builder_cls, mock_popen, mock_session_service
    ):
        """Test generic RuntimeError for unexpected errors (line 165)."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        # Raise exception during output processing (inside the try block)
        mock_process.stdout.readline.side_effect = Exception("Unexpected crash")

        with pytest.raises(
            RuntimeError, match="An unexpected error occurred: Unexpected crash"
        ):
            call_gemini_cli(mock_session_service)


class TestGeminiCliAgent:
    """Tests for GeminiCliAgent class."""

    def test_init(self, mock_session_service):
        """Test initialization."""
        agent = GeminiCliAgent(mock_session_service)
        assert agent.session_service == mock_session_service

    @patch("pipe.core.delegates.gemini_cli_delegate.run")
    def test_run_success(
        self,
        mock_delegate_run,
        mock_session_service,
        mock_session_turn_service,
        mock_timestamp,
    ):
        """Test successful run of GeminiCliAgent."""
        # Setup mocks
        mock_delegate_run.return_value = ("Response text", 100, {"total_tokens": 100})

        session = SessionFactory.create()
        mock_session_service.get_session.return_value = session

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test instruction")

        # Execute
        response, token_count, turns, thought = agent.run(args, mock_session_service)

        # Verify
        assert response == "Response text"
        assert token_count == 100
        assert len(turns) == 1
        assert isinstance(turns[0], ModelResponseTurn)
        assert turns[0].content == "Response text"
        assert thought is None

        # Verify cumulative stats update
        assert session.cumulative_total_tokens == 100
        mock_session_service.repository.save.assert_called_once_with(session)

    @patch("pipe.core.delegates.gemini_cli_delegate.run")
    @patch("builtins.print")
    def test_run_text_format(
        self,
        mock_print,
        mock_delegate_run,
        mock_session_service,
        mock_session_turn_service,
        mock_timestamp,
    ):
        """Test run with text output format."""
        mock_delegate_run.return_value = ("Response text", 100, None)

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test", output_format="text")

        agent.run(args, mock_session_service)

        mock_print.assert_called_once_with("Response text")

    @patch("pipe.core.delegates.gemini_cli_delegate.run")
    def test_run_stream_json_format(
        self,
        mock_delegate_run,
        mock_session_service,
        mock_session_turn_service,
        mock_timestamp,
    ):
        """Test run with stream-json output format (line 222)."""
        mock_delegate_run.return_value = ("Response text", 100, None)

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test", output_format="stream-json")

        agent.run(args, mock_session_service)

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    @patch("pipe.core.services.gemini_tool_service.GeminiToolService")
    @patch("pipe.core.domains.gemini_token_count.create_local_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.count_tokens")
    @patch("pipe.core.domains.gemini_cli_stream_processor.GeminiCliStreamProcessor")
    @patch("pipe.core.delegates.gemini_cli_delegate._reconcile_tool_calls")
    def test_run_stream_success(
        self,
        mock_reconcile,
        mock_processor_cls,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_tool_service_cls,
        mock_builder_cls,
        mock_popen,
        mock_session_service,
        mock_session_turn_service,
        mock_timestamp,
    ):
        """Test successful run_stream of GeminiCliAgent."""
        # Setup mocks
        mock_builder = mock_builder_cls.return_value
        mock_builder.build.return_value = '{"prompt": "test"}'

        mock_count_tokens.return_value = 50

        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [
            '{"type": "message", "role": "assistant", "delta": true, "content": "Hello"}',
            '{"type": "message", "role": "assistant", "delta": true, "content": " world"}',
            "",
        ]
        mock_process.stderr.read.return_value = ""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        mock_processor = mock_processor_cls.return_value
        mock_result = MagicMock()
        mock_result.response = "Hello world"
        mock_result.stats = {"total_tokens": 60, "cached": 20}
        mock_processor.get_result.return_value = mock_result

        session = SessionFactory.create()
        mock_session_service.get_session.return_value = session

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test instruction")

        # Execute
        results = list(agent.run_stream(args, mock_session_service))

        # Verify yields
        assert results[0] == ""
        assert results[1] == "Hello"
        assert results[2] == " world"

        final_result = results[3]
        assert final_result[0] == "end"
        assert final_result[1] == "Hello world"
        assert final_result[2] == 50
        assert len(final_result[3]) == 1
        assert final_result[3][0].content == "Hello world"

        # Verify cumulative stats update
        assert session.cumulative_total_tokens == 60
        assert session.cumulative_cached_tokens == 20
        mock_session_service.repository.save.assert_called_once_with(session)
        mock_reconcile.assert_called_once()
        mock_session_turn_service.merge_pool_into_turns.assert_called_once()

    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_run_stream_missing_model_name(
        self, mock_builder_cls, mock_session_service
    ):
        """Test run_stream raises ValueError when model name is missing (line 302)."""
        mock_session_service.settings.model.name = None
        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test")
        generator = agent.run_stream(args, mock_session_service)

        # First yield is empty string
        assert next(generator) == ""

        with pytest.raises(ValueError, match="'model' not found in settings"):
            next(generator)

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    def test_run_stream_command_not_found(
        self, mock_builder_cls, mock_popen, mock_session_service
    ):
        """Test run_stream raises RuntimeError when gemini command is not found (lines 337-338)."""
        mock_popen.side_effect = FileNotFoundError()
        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test")
        generator = agent.run_stream(args, mock_session_service)

        # Skip the first empty yield
        next(generator)

        with pytest.raises(RuntimeError, match="gemini' command not found"):
            next(generator)

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    @patch("pipe.core.services.gemini_tool_service.GeminiToolService")
    @patch("pipe.core.domains.gemini_token_count.create_local_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.count_tokens")
    @patch("pipe.core.domains.gemini_cli_stream_processor.GeminiCliStreamProcessor")
    def test_run_stream_invalid_json_chunk(
        self,
        mock_processor_cls,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_tool_service_cls,
        mock_builder_cls,
        mock_popen,
        mock_session_service,
        mock_timestamp,
    ):
        """Test run_stream handles invalid JSON chunks (line 357)."""
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = ["invalid json", ""]
        mock_process.stderr.read.return_value = ""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        mock_processor = mock_processor_cls.return_value
        mock_processor.get_result.return_value = MagicMock(response="", stats=None)

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test")
        results = list(agent.run_stream(args, mock_session_service))

        assert len(results) == 2  # ["", ("end", ...)]

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    @patch("pipe.core.services.gemini_tool_service.GeminiToolService")
    @patch("pipe.core.domains.gemini_token_count.create_local_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.count_tokens")
    @patch("pipe.core.domains.gemini_cli_stream_processor.GeminiCliStreamProcessor")
    def test_run_stream_no_stdout(
        self,
        mock_processor_cls,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_tool_service_cls,
        mock_builder_cls,
        mock_popen,
        mock_session_service,
        mock_timestamp,
    ):
        """Test run_stream when stdout is None (lines 337-338)."""
        mock_process = MagicMock()
        mock_process.stdout = None
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        mock_processor = mock_processor_cls.return_value
        mock_processor.get_result.return_value = MagicMock(response="", stats=None)

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test")
        list(agent.run_stream(args, mock_session_service))

    @patch("pipe.core.agents.gemini_cli.subprocess.Popen")
    @patch("pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder")
    @patch("pipe.core.services.gemini_tool_service.GeminiToolService")
    @patch("pipe.core.domains.gemini_token_count.create_local_tokenizer")
    @patch("pipe.core.domains.gemini_token_count.count_tokens")
    @patch("pipe.core.domains.gemini_cli_stream_processor.GeminiCliStreamProcessor")
    def test_run_stream_execution_error(
        self,
        mock_processor_cls,
        mock_count_tokens,
        mock_create_tokenizer,
        mock_tool_service_cls,
        mock_builder_cls,
        mock_popen,
        mock_session_service,
        mock_timestamp,
    ):
        """Test run_stream raises RuntimeError on non-zero exit code (line 384)."""
        mock_process = MagicMock()
        mock_process.stdout.readline.return_value = ""
        mock_process.stderr.read.return_value = "Run stream error"
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test")
        generator = agent.run_stream(args, mock_session_service)

        # Consume generator
        with pytest.raises(
            RuntimeError, match="Error during gemini-cli execution: Run stream error"
        ):
            list(generator)
