# Delegates Layer Testing Strategy

**Layer:** `src/pipe/core/delegates/`

## Responsibilities
- Command execution entry points
- Coordination between command-line arguments and service layer
- Simple orchestration of services to fulfill specific commands (fork, dry-run, help, etc.)
- Output formatting for CLI responses

## Testing Strategy
- **Mock the Service Layer**: Mock all service dependencies (SessionService, PromptService, etc.)
- **Focus**:
  - Command execution flow
  - Argument validation and error handling
  - Service coordination logic
  - Output verification (printed messages, returned values)
- **Testing Style**: Use fixtures to create mock services and test each delegate's `run()` function with various argument scenarios

## Delegate Characteristics
Delegates are lightweight command handlers that:
- Take parsed command-line arguments (`TaktArgs`, `Settings`, etc.)
- Instantiate or receive service objects
- Call service methods to execute business logic
- Handle errors and format output for the CLI
- Do NOT contain complex business logic (that belongs in services)

## Test Patterns

### Pattern 1: Simple Delegate (e.g., help_delegate)

```python
# tests/unit/core/delegates/test_help_delegate.py
import pytest
from unittest.mock import Mock
from pipe.core.delegates import help_delegate


class TestHelpDelegate:
    """Test help_delegate.run() function."""

    def test_run_prints_help(self, capsys):
        """Test that run() prints help message."""
        mock_parser = Mock()
        mock_parser.print_help = Mock()

        help_delegate.run(mock_parser)

        mock_parser.print_help.assert_called_once()
```

### Pattern 2: Service-Coordinating Delegate (e.g., fork_delegate)

```python
# tests/unit/core/delegates/test_fork_delegate.py
import pytest
from unittest.mock import Mock, patch
from pipe.core.delegates import fork_delegate
from pipe.core.models.args import TaktArgs
from pipe.core.models.settings import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = Mock(spec=Settings)
    settings.timezone = "Asia/Tokyo"
    return settings


@pytest.fixture
def mock_workflow_service():
    """Create mock SessionWorkflowService."""
    service = Mock()
    service.fork_session = Mock()
    return service


class TestForkDelegate:
    """Test fork_delegate.run() function."""

    @patch('pipe.core.delegates.fork_delegate.ServiceFactory')
    def test_run_successful_fork(self, mock_factory_cls, mock_settings, mock_workflow_service, capsys):
        """Test successful session fork."""
        # Setup mock factory
        mock_factory = Mock()
        mock_factory.create_session_workflow_service.return_value = mock_workflow_service
        mock_factory_cls.return_value = mock_factory

        # Create args
        args = TaktArgs(
            fork="source-session-123",
            at_turn=5,
        )

        # Execute
        fork_delegate.run(args, "/tmp/project", mock_settings)

        # Verify service was called correctly
        mock_workflow_service.fork_session.assert_called_once_with("source-session-123", 4)  # at_turn - 1

        # Verify output message
        captured = capsys.readouterr()
        assert "Successfully forked session source-session-123 at turn 5" in captured.out

    @patch('pipe.core.delegates.fork_delegate.ServiceFactory')
    def test_run_missing_at_turn_raises_error(self, mock_factory_cls, mock_settings):
        """Test that missing --at-turn raises ValueError."""
        args = TaktArgs(
            fork="source-session-123",
            at_turn=None,  # Missing required argument
        )

        with pytest.raises(ValueError, match="--at-turn is required"):
            fork_delegate.run(args, "/tmp/project", mock_settings)

    @patch('pipe.core.delegates.fork_delegate.ServiceFactory')
    def test_run_session_not_found(self, mock_factory_cls, mock_settings, mock_workflow_service):
        """Test error handling when session is not found."""
        # Setup mock to raise FileNotFoundError
        mock_workflow_service.fork_session.side_effect = FileNotFoundError("Session not found")
        mock_factory = Mock()
        mock_factory.create_session_workflow_service.return_value = mock_workflow_service
        mock_factory_cls.return_value = mock_factory

        args = TaktArgs(
            fork="nonexistent-session",
            at_turn=5,
        )

        with pytest.raises(ValueError, match="Session not found"):
            fork_delegate.run(args, "/tmp/project", mock_settings)

    @patch('pipe.core.delegates.fork_delegate.ServiceFactory')
    def test_run_invalid_turn_index(self, mock_factory_cls, mock_settings, mock_workflow_service):
        """Test error handling for invalid turn index."""
        # Setup mock to raise IndexError
        mock_workflow_service.fork_session.side_effect = IndexError("Turn index out of range")
        mock_factory = Mock()
        mock_factory.create_session_workflow_service.return_value = mock_workflow_service
        mock_factory_cls.return_value = mock_factory

        args = TaktArgs(
            fork="source-session-123",
            at_turn=999,  # Invalid turn number
        )

        with pytest.raises(ValueError, match="Turn index out of range"):
            fork_delegate.run(args, "/tmp/project", mock_settings)
```

### Pattern 3: Output-Generating Delegate (e.g., dry_run_delegate)

```python
# tests/unit/core/delegates/test_dry_run_delegate.py
import pytest
import json
from unittest.mock import Mock, patch
from pipe.core.delegates import dry_run_delegate
from pipe.core.models.prompt import PromptModel


@pytest.fixture
def mock_session_service():
    """Create mock SessionService."""
    service = Mock()
    service.settings = Mock()
    service.settings.api_mode = "gemini-api"
    return service


@pytest.fixture
def mock_prompt_service():
    """Create mock PromptService."""
    service = Mock()
    service.jinja_env = Mock()
    return service


@pytest.fixture
def mock_prompt_model():
    """Create mock PromptModel."""
    return PromptModel(
        session_id="test-123",
        purpose="Test purpose",
        background="Test background",
        turns=[],
        references=[],
    )


class TestDryRunDelegate:
    """Test dry_run_delegate.run() function."""

    def test_run_prints_json_prompt(self, mock_session_service, mock_prompt_service, mock_prompt_model, capsys):
        """Test that run() prints formatted JSON prompt."""
        # Setup prompt service to return prompt model
        mock_prompt_service.build_prompt.return_value = mock_prompt_model

        # Setup jinja template
        mock_template = Mock()
        mock_template.render.return_value = json.dumps({
            "session_id": "test-123",
            "purpose": "Test purpose",
        })
        mock_prompt_service.jinja_env.get_template.return_value = mock_template

        # Execute
        dry_run_delegate.run(mock_session_service, mock_prompt_service)

        # Verify service methods were called
        mock_prompt_service.build_prompt.assert_called_once_with(mock_session_service)
        mock_prompt_service.jinja_env.get_template.assert_called_once_with("gemini_api_prompt.j2")
        mock_template.render.assert_called_once()

        # Verify JSON output
        captured = capsys.readouterr()
        output_json = json.loads(captured.out)
        assert output_json["session_id"] == "test-123"
        assert output_json["purpose"] == "Test purpose"

    def test_run_uses_cli_template_for_cli_mode(self, mock_session_service, mock_prompt_service, mock_prompt_model):
        """Test that CLI mode uses gemini_cli_prompt.j2 template."""
        # Change api_mode to CLI
        mock_session_service.settings.api_mode = "gemini-cli"
        mock_prompt_service.build_prompt.return_value = mock_prompt_model

        mock_template = Mock()
        mock_template.render.return_value = json.dumps({"test": "data"})
        mock_prompt_service.jinja_env.get_template.return_value = mock_template

        # Execute
        dry_run_delegate.run(mock_session_service, mock_prompt_service)

        # Verify CLI template was used
        mock_prompt_service.jinja_env.get_template.assert_called_once_with("gemini_cli_prompt.j2")

    def test_run_handles_empty_prompt(self, mock_session_service, mock_prompt_service):
        """Test handling of empty prompt model."""
        # Setup empty prompt model
        empty_prompt = PromptModel(
            session_id="empty",
            purpose="",
            background="",
            turns=[],
            references=[],
        )
        mock_prompt_service.build_prompt.return_value = empty_prompt

        mock_template = Mock()
        mock_template.render.return_value = json.dumps({"session_id": "empty"})
        mock_prompt_service.jinja_env.get_template.return_value = mock_template

        # Execute (should not raise)
        dry_run_delegate.run(mock_session_service, mock_prompt_service)

        # Verify it was called successfully
        mock_prompt_service.build_prompt.assert_called_once()
```

### Pattern 4: Complex Streaming Delegate (e.g., gemini_api_delegate)

```python
# tests/unit/core/delegates/test_gemini_api_delegate.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from pipe.core.delegates import gemini_api_delegate
from pipe.core.models.args import TaktArgs
from pipe.core.models.unified_chunk import TextChunk, ToolCallChunk, MetadataChunk, UsageMetadata


@pytest.fixture
def mock_session_service():
    """Create mock SessionService."""
    service = Mock()
    service.current_session = Mock()
    service.current_session_id = "test-session-123"
    service.current_session.cached_content_token_count = 1000
    service.current_session.cumulative_total_tokens = 5000
    service.current_session.cumulative_cached_tokens = 1000
    service.settings = Mock()
    service.settings.max_tool_calls = 10
    service.timezone_obj = Mock()
    service.project_root = "/tmp/test"
    service.repository = Mock()
    service.get_session = Mock(return_value=service.current_session)
    return service


@pytest.fixture
def mock_session_turn_service():
    """Create mock SessionTurnService."""
    service = Mock()
    service.merge_pool_into_turns = Mock()
    return service


@pytest.fixture
def mock_args():
    """Create mock TaktArgs."""
    return TaktArgs(
        instruction="Test instruction",
        session="test-session-123",
    )


class TestGeminiApiDelegate:
    """Test gemini_api_delegate.run_stream() function."""

    @patch('pipe.core.delegates.gemini_api_delegate.GeminiApiAgent')
    @patch('pipe.core.delegates.gemini_api_delegate.StreamingLogRepository')
    @patch('pipe.core.delegates.gemini_api_delegate.execute_tool')
    def test_run_stream_text_only_response(
        self,
        mock_execute_tool,
        mock_log_repo_cls,
        mock_agent_cls,
        mock_session_service,
        mock_session_turn_service,
        mock_args,
    ):
        """Test streaming a simple text-only response."""
        # Setup mock agent
        mock_agent = Mock()
        mock_agent.last_raw_response = {"test": "raw_response"}
        mock_agent.last_cached_turn_count = 5

        # Setup streaming response
        mock_agent.stream_content.return_value = iter([
            TextChunk(content="Hello ", is_thought=False),
            TextChunk(content="world!", is_thought=False),
            MetadataChunk(
                usage=UsageMetadata(
                    prompt_token_count=100,
                    candidates_token_count=10,
                    total_token_count=110,
                    cached_content_token_count=50,
                )
            ),
        ])
        mock_agent_cls.return_value = mock_agent

        # Execute stream
        result = list(gemini_api_delegate.run_stream(
            mock_args,
            mock_session_service,
            mock_session_turn_service,
        ))

        # Verify streamed chunks
        assert "Hello " in result
        assert "world!" in result

        # Verify final tuple
        final = result[-1]
        assert final[0] == "end"
        assert "Hello world!" in final[1]  # Full text
        assert final[2] > 0  # token_count
        assert len(final[3]) > 0  # intermediate_turns

    @patch('pipe.core.delegates.gemini_api_delegate.GeminiApiAgent')
    @patch('pipe.core.delegates.gemini_api_delegate.StreamingLogRepository')
    @patch('pipe.core.delegates.gemini_api_delegate.execute_tool')
    def test_run_stream_with_tool_call(
        self,
        mock_execute_tool,
        mock_log_repo_cls,
        mock_agent_cls,
        mock_session_service,
        mock_session_turn_service,
        mock_args,
    ):
        """Test streaming response with tool call."""
        # Setup tool execution
        mock_execute_tool.return_value = {"message": "Tool executed successfully"}

        # Setup mock agent with two responses (tool call, then final text)
        mock_agent = Mock()
        mock_agent.last_raw_response = {"test": "raw"}
        mock_agent.last_cached_turn_count = 5

        # First response: tool call
        first_stream = iter([
            TextChunk(content="I'll call a tool", is_thought=False),
            ToolCallChunk(name="test_tool", args={"param": "value"}),
            MetadataChunk(
                usage=UsageMetadata(
                    prompt_token_count=100,
                    candidates_token_count=10,
                    total_token_count=110,
                    cached_content_token_count=50,
                )
            ),
        ])

        # Second response: final text
        second_stream = iter([
            TextChunk(content="Tool completed", is_thought=False),
            MetadataChunk(
                usage=UsageMetadata(
                    prompt_token_count=120,
                    candidates_token_count=15,
                    total_token_count=135,
                    cached_content_token_count=60,
                )
            ),
        ])

        mock_agent.stream_content.side_effect = [first_stream, second_stream]
        mock_agent_cls.return_value = mock_agent

        # Execute stream
        result = list(gemini_api_delegate.run_stream(
            mock_args,
            mock_session_service,
            mock_session_turn_service,
        ))

        # Verify tool execution
        mock_execute_tool.assert_called_once_with("test_tool", {"param": "value"})

        # Verify tool call markdown was streamed
        tool_call_output = "".join([r for r in result if isinstance(r, str)])
        assert "Tool call: test_tool" in tool_call_output
        assert "Tool status:" in tool_call_output

    @patch('pipe.core.delegates.gemini_api_delegate.GeminiApiAgent')
    @patch('pipe.core.delegates.gemini_api_delegate.StreamingLogRepository')
    def test_run_stream_max_tool_calls_exceeded(
        self,
        mock_log_repo_cls,
        mock_agent_cls,
        mock_session_service,
        mock_session_turn_service,
        mock_args,
    ):
        """Test that streaming stops when max tool calls is exceeded."""
        # Set low max_tool_calls
        mock_session_service.settings.max_tool_calls = 2

        mock_agent = Mock()
        mock_agent.last_raw_response = {"test": "raw"}

        # Setup agent to always return tool calls
        def create_tool_stream():
            return iter([
                ToolCallChunk(name="test_tool", args={}),
                MetadataChunk(
                    usage=UsageMetadata(
                        prompt_token_count=100,
                        candidates_token_count=10,
                        total_token_count=110,
                        cached_content_token_count=50,
                    )
                ),
            ])

        mock_agent.stream_content.side_effect = [create_tool_stream() for _ in range(5)]
        mock_agent_cls.return_value = mock_agent

        with patch('pipe.core.delegates.gemini_api_delegate.execute_tool') as mock_execute:
            mock_execute.return_value = {"message": "OK"}

            # Execute stream
            result = list(gemini_api_delegate.run_stream(
                mock_args,
                mock_session_service,
                mock_session_turn_service,
            ))

            # Verify max tool calls error message
            result_str = "".join([r for r in result if isinstance(r, str)])
            assert "Maximum number of tool calls reached" in result_str

    @patch('pipe.core.delegates.gemini_api_delegate.GeminiApiAgent')
    @patch('pipe.core.delegates.gemini_api_delegate.StreamingLogRepository')
    def test_run_stream_with_thoughts(
        self,
        mock_log_repo_cls,
        mock_agent_cls,
        mock_session_service,
        mock_session_turn_service,
        mock_args,
    ):
        """Test streaming response with thought content."""
        mock_agent = Mock()
        mock_agent.last_raw_response = {"test": "raw"}
        mock_agent.last_cached_turn_count = 5

        # Setup stream with thoughts and regular text
        mock_agent.stream_content.return_value = iter([
            TextChunk(content="<thinking>Internal thought</thinking>", is_thought=True),
            TextChunk(content="Visible response", is_thought=False),
            MetadataChunk(
                usage=UsageMetadata(
                    prompt_token_count=100,
                    candidates_token_count=10,
                    total_token_count=110,
                    cached_content_token_count=50,
                )
            ),
        ])
        mock_agent_cls.return_value = mock_agent

        # Execute stream
        result = list(gemini_api_delegate.run_stream(
            mock_args,
            mock_session_service,
            mock_session_turn_service,
        ))

        # Verify both thought and regular text were processed
        # Note: thoughts are streamed to user but stored separately
        result_str = "".join([r for r in result if isinstance(r, str)])
        assert "Internal thought" in result_str
        assert "Visible response" in result_str

        # Verify final tuple has thought field
        final = result[-1]
        assert final[4] is not None  # thought field
```

## Mandatory Test Items
- ✅ Successful execution of each delegate's main flow
- ✅ Argument validation (missing required args, invalid values)
- ✅ Error handling and propagation (FileNotFoundError, ValueError, etc.)
- ✅ Service method calls with correct parameters
- ✅ Output verification (console output, return values)
- ✅ For streaming delegates: chunk processing, tool execution, max iterations
- ✅ Edge cases (empty responses, concurrent state changes, etc.)

## Testing Guidelines

### Do's:
- Mock all service dependencies (SessionService, PromptService, etc.)
- Use `capsys` fixture to verify console output
- Test both success and failure paths
- Verify service methods are called with correct arguments
- Test argument validation before service calls
- For streaming delegates: test chunks are yielded correctly

### Don'ts:
- Don't test service implementation details (those belong in service tests)
- Don't use actual file system (use mocks)
- Don't skip error cases
- Don't test complex business logic (delegates should be thin orchestrators)

## Common Test Fixtures

```python
@pytest.fixture
def mock_settings():
    """Standard mock settings for delegate tests."""
    settings = Mock(spec=Settings)
    settings.timezone = "Asia/Tokyo"
    settings.api_mode = "gemini-api"
    settings.max_tool_calls = 10
    return settings


@pytest.fixture
def mock_session_service():
    """Standard mock SessionService for delegate tests."""
    service = Mock()
    service.current_session = Mock()
    service.current_session_id = "test-session-123"
    service.settings = mock_settings()
    service.project_root = "/tmp/test"
    return service


@pytest.fixture
def mock_args():
    """Standard mock TaktArgs for delegate tests."""
    return TaktArgs(
        instruction="Test instruction",
        session="test-session-123",
    )
```
