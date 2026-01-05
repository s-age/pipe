# Agents Layer Testing Strategy

**Layer:** `src/pipe/core/agents/`

## Responsibilities
- External AI model integrations (Gemini API, Gemini CLI)
- Streaming and non-streaming response handling
- Agent registry and auto-discovery system
- Subprocess management for CLI-based agents
- Tool service coordination
- Payload delegation to domain classes

## Testing Strategy
- **Mock External Dependencies**: Mock API clients, subprocess calls, and domain services
- **Focus**:
  - Agent registry registration and lookup
  - Delegation to domain classes (payload builders, stream processors)
  - Delegation to workflow coordinators (delegates)
  - Tool service integration
  - Subprocess management and process tracking
  - Return value structure validation
- **Testing Style**: Use fixtures to create mock dependencies and test agent methods with various scenarios

## Agent Characteristics
Agents are integration adapters that:
- Implement `BaseAgent` interface with `run()` method
- Register themselves using `@register_agent(key)` decorator
- Delegate payload construction to domain classes
- Use tool services for tool loading and conversion
- Coordinate with delegates for complete workflows
- Handle streaming with generators
- Return standardized tuple: `(response_text, token_count, turns_to_save, thought_text)`
- Do NOT contain business logic (that belongs in domains)
- Do NOT contain workflow orchestration (that belongs in delegates)

## Test Patterns

### Pattern 1: Agent Registry Testing

Test the plugin-like auto-discovery and registration system.

```python
# tests/unit/core/agents/test_agent_registry.py
import pytest
from pipe.core.agents import AGENT_REGISTRY, get_agent_class, register_agent
from pipe.core.agents.base import BaseAgent


class TestAgentRegistry:
    """Test agent registry system."""

    def test_gemini_api_agent_is_registered(self):
        """Test GeminiApiAgent is registered in registry."""
        assert "gemini-api" in AGENT_REGISTRY
        agent_cls = AGENT_REGISTRY["gemini-api"]
        assert agent_cls.__name__ == "GeminiApiAgent"

    def test_gemini_cli_agent_is_registered(self):
        """Test GeminiCliAgent is registered in registry."""
        assert "gemini-cli" in AGENT_REGISTRY
        agent_cls = AGENT_REGISTRY["gemini-cli"]
        assert agent_cls.__name__ == "GeminiCliAgent"

    def test_get_agent_class_returns_correct_class(self):
        """Test get_agent_class returns correct agent class."""
        agent_cls = get_agent_class("gemini-api")
        assert agent_cls.__name__ == "GeminiApiAgent"

    def test_get_agent_class_raises_for_unknown_key(self):
        """Test get_agent_class raises ValueError for unknown key."""
        with pytest.raises(ValueError, match="Unknown api_mode: 'invalid-agent'"):
            get_agent_class("invalid-agent")

    def test_register_agent_decorator_adds_to_registry(self):
        """Test @register_agent decorator adds agent to registry."""
        @register_agent("test-agent")
        class TestAgent(BaseAgent):
            def run(self, args, session_service):
                return ("test", None, [], None)

        assert "test-agent" in AGENT_REGISTRY
        assert AGENT_REGISTRY["test-agent"] == TestAgent
```

### Pattern 2: Gemini API Agent Testing

Test API-based agent with delegation to domain classes and delegates.

```python
# tests/unit/core/agents/test_gemini_api_agent.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from pipe.core.agents.gemini_api import GeminiApiAgent
from pipe.core.models.args import TaktArgs


@pytest.fixture
def mock_session_service():
    """Create mock SessionService."""
    service = Mock()
    service.settings = Mock()
    service.settings.model.name = "gemini-2.0-flash-exp"
    service.settings.timezone = "Asia/Tokyo"
    service.settings.parameters = Mock()
    service.project_root = "/tmp/test"
    service.current_session = Mock()
    service.current_session.session_id = "test-session"
    return service


@pytest.fixture
def mock_tool_service():
    """Create mock GeminiToolService."""
    service = Mock()
    service.load_tools = Mock(return_value=[])
    service.convert_to_genai_tools = Mock(return_value=[])
    return service


class TestGeminiApiAgent:
    """Test GeminiApiAgent class."""

    def test_initialization_with_default_tool_service(self, mock_session_service):
        """Test agent initializes with default GeminiToolService."""
        agent = GeminiApiAgent(mock_session_service)

        assert agent.session_service == mock_session_service
        assert agent.tool_service is not None
        assert agent.payload_service is not None

    def test_initialization_with_custom_tool_service(self, mock_session_service, mock_tool_service):
        """Test agent initializes with injected tool service."""
        agent = GeminiApiAgent(mock_session_service, tool_service=mock_tool_service)

        assert agent.tool_service == mock_tool_service

    @patch('pipe.core.delegates.gemini_api_delegate.run_stream')
    def test_run_delegates_to_gemini_api_delegate(
        self,
        mock_run_stream,
        mock_session_service,
        mock_tool_service
    ):
        """Test run() delegates to gemini_api_delegate.run_stream()."""
        # Setup mock delegate response
        mock_run_stream.return_value = [
            ("chunk1", None, None, [], None),
            ("chunk2", None, None, [], None),
            ("end", "Final response", 150, [Mock()], "Thought process"),
        ]

        agent = GeminiApiAgent(mock_session_service, tool_service=mock_tool_service)
        args = TaktArgs(instruction="Test instruction")

        response, token_count, turns, thought = agent.run(args, mock_session_service)

        # Verify delegation
        mock_run_stream.assert_called_once()
        assert response == "Final response"
        assert token_count == 150
        assert len(turns) == 1
        assert thought == "Thought process"

    @patch('pipe.core.delegates.gemini_api_delegate.run_stream')
    def test_run_stream_yields_from_delegate(
        self,
        mock_run_stream,
        mock_session_service,
        mock_tool_service
    ):
        """Test run_stream() yields from gemini_api_delegate."""
        mock_run_stream.return_value = iter([
            ("chunk1", None, None, [], None),
            ("chunk2", None, None, [], None),
        ])

        agent = GeminiApiAgent(mock_session_service, tool_service=mock_tool_service)
        args = TaktArgs(instruction="Test instruction")

        results = list(agent.run_stream(args, mock_session_service))

        assert len(results) == 2
        mock_run_stream.assert_called_once()

    @patch('pipe.core.agents.gemini_api.genai.Client')
    def test_stream_content_uses_tool_service(
        self,
        mock_client_cls,
        mock_session_service,
        mock_tool_service
    ):
        """Test stream_content() uses tool service for tool loading."""
        agent = GeminiApiAgent(mock_session_service, tool_service=mock_tool_service)

        # Mock payload service to avoid actual API call
        with patch.object(agent.payload_service, 'prepare_request') as mock_prepare:
            mock_prepare.return_value = ([], None)
            with patch.object(agent, '_build_generation_config'):
                with patch.object(agent, '_execute_streaming_call', return_value=iter([])):
                    list(agent.stream_content())

        mock_tool_service.load_tools.assert_called_once_with(agent.project_root)
        mock_tool_service.convert_to_genai_tools.assert_called_once()

    def test_stream_content_delegates_to_payload_service(
        self,
        mock_session_service,
        mock_tool_service
    ):
        """Test stream_content() delegates payload preparation to domain class."""
        agent = GeminiApiAgent(mock_session_service, tool_service=mock_tool_service)

        with patch.object(agent.payload_service, 'prepare_request') as mock_prepare:
            mock_prepare.return_value = ([], None)
            with patch.object(agent, '_build_generation_config'):
                with patch.object(agent, '_execute_streaming_call', return_value=iter([])):
                    list(agent.stream_content())

        # Verify payload service was called
        mock_prepare.assert_called_once()
```

### Pattern 3: Gemini CLI Agent Testing

Test CLI-based agent with subprocess delegation.

```python
# tests/unit/core/agents/test_gemini_cli_agent.py
import pytest
from unittest.mock import Mock, patch
from pipe.core.agents.gemini_cli import GeminiCliAgent
from pipe.core.models.args import TaktArgs


@pytest.fixture
def mock_session_service():
    """Create mock SessionService."""
    service = Mock()
    service.settings = Mock()
    service.settings.model.name = "gemini-2.0-flash-exp"
    service.settings.timezone = "Asia/Tokyo"
    service.project_root = "/tmp/test"
    service.current_session_id = "test-session"
    service.timezone_obj = Mock()
    return service


class TestGeminiCliAgent:
    """Test GeminiCliAgent class."""

    def test_initialization(self, mock_session_service):
        """Test agent initializes with session service."""
        agent = GeminiCliAgent(mock_session_service)

        assert agent.session_service == mock_session_service

    @patch('pipe.core.delegates.gemini_cli_delegate.run')
    def test_run_delegates_to_gemini_cli_delegate(
        self,
        mock_run,
        mock_session_service
    ):
        """Test run() delegates to gemini_cli_delegate.run()."""
        # Setup mock delegate response
        mock_run.return_value = (
            "Model response text",
            120,
            {"total_tokens": 120, "cached": 50}
        )

        # Mock session repository
        mock_session_service.get_session = Mock(return_value=Mock(
            cumulative_total_tokens=0,
            cumulative_cached_tokens=0
        ))
        mock_session_service.repository.save = Mock()

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test instruction", output_format="json")

        response, token_count, turns, thought = agent.run(args, mock_session_service)

        # Verify delegation
        mock_run.assert_called_once()
        assert response == "Model response text"
        assert token_count == 120
        assert len(turns) == 1
        assert turns[0].type == "model_response"
        assert thought is None

    @patch('pipe.core.delegates.gemini_cli_delegate.run')
    def test_run_updates_cumulative_tokens(
        self,
        mock_run,
        mock_session_service
    ):
        """Test run() updates cumulative token stats in session."""
        mock_run.return_value = (
            "Response",
            100,
            {"total_tokens": 100, "cached": 30}
        )

        mock_session = Mock(
            cumulative_total_tokens=50,
            cumulative_cached_tokens=10
        )
        mock_session_service.get_session = Mock(return_value=mock_session)
        mock_session_service.repository.save = Mock()

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test", output_format="json")

        agent.run(args, mock_session_service)

        # Verify cumulative stats updated
        assert mock_session.cumulative_total_tokens == 150  # 50 + 100
        assert mock_session.cumulative_cached_tokens == 40   # 10 + 30
        mock_session_service.repository.save.assert_called_once_with(mock_session)

    @patch('pipe.core.agents.gemini_cli.subprocess.Popen')
    @patch('pipe.core.domains.gemini_cli_payload.GeminiCliPayloadBuilder')
    def test_run_stream_streams_output(
        self,
        mock_builder_cls,
        mock_popen,
        mock_session_service
    ):
        """Test run_stream() streams output from subprocess."""
        # Mock payload builder
        mock_builder = Mock()
        mock_builder.build.return_value = '{"prompt": "test"}'
        mock_builder_cls.return_value = mock_builder

        # Mock subprocess
        mock_process = Mock()
        mock_process.stdout = iter(['{"type":"message","delta":"chunk1"}\n', '{"type":"message","delta":"chunk2"}\n'])
        mock_process.stderr.read.return_value = ""
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        agent = GeminiCliAgent(mock_session_service)
        args = TaktArgs(instruction="Test", output_format="stream-json")

        # Mock dependencies
        with patch('pipe.core.domains.gemini_token_count.create_local_tokenizer'):
            with patch('pipe.core.domains.gemini_token_count.count_tokens', return_value=50):
                with patch('pipe.core.services.gemini_tool_service.GeminiToolService'):
                    with patch('pipe.core.repositories.streaming_log_repository.StreamingLogRepository'):
                        results = list(agent.run_stream(args, mock_session_service))

        # Verify streaming occurred
        assert len(results) > 0
        mock_popen.assert_called_once()
```

### Pattern 4: Takt Agent Testing (Subprocess Management)

Test subprocess-based agent with process management.

```python
# tests/unit/core/agents/test_takt_agent.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from pipe.core.agents.takt_agent import TaktAgent


@pytest.fixture
def mock_settings():
    """Create mock Settings."""
    settings = Mock()
    settings.timezone = "Asia/Tokyo"
    return settings


@pytest.fixture
def agent(mock_settings):
    """Create TaktAgent instance."""
    return TaktAgent(project_root="/tmp/test", settings=mock_settings)


class TestTaktAgent:
    """Test TaktAgent class."""

    @patch('pipe.core.agents.takt_agent.subprocess.run')
    def test_run_new_session_success(self, mock_run, agent):
        """Test run_new_session creates session successfully."""
        # Mock successful execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"session_id": "new-session-123"}\n'
        mock_result.stderr = "New session created: new-session-123\n"
        mock_run.return_value = mock_result

        session_id, stdout, stderr = agent.run_new_session(
            purpose="Test purpose",
            background="Test background",
            roles="roles.yml",
            instruction="Test instruction"
        )

        assert session_id == "new-session-123"
        assert stdout == '{"session_id": "new-session-123"}\n'
        mock_run.assert_called_once()

    @patch('pipe.core.agents.takt_agent.subprocess.run')
    def test_run_new_session_with_multi_step_reasoning(self, mock_run, agent):
        """Test run_new_session includes --multi-step-reasoning flag."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"session_id": "test-session"}\n'
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        agent.run_new_session(
            purpose="Test",
            background="Test",
            roles="roles.yml",
            instruction="Test",
            multi_step_reasoning=True
        )

        # Verify --multi-step-reasoning was included in command
        call_args = mock_run.call_args
        command = call_args[0][0]
        assert "--multi-step-reasoning" in command

    @patch('pipe.core.agents.takt_agent.subprocess.run')
    def test_run_new_session_command_failure(self, mock_run, agent):
        """Test run_new_session raises RuntimeError on command failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: Something went wrong"
        mock_run.return_value = mock_result

        with pytest.raises(RuntimeError, match="takt command failed with return code 1"):
            agent.run_new_session(
                purpose="Test",
                background="Test",
                roles="roles.yml",
                instruction="Test"
            )

    @patch('pipe.core.services.process_manager_service.ProcessManagerService')
    @patch('pipe.core.agents.takt_agent.subprocess.run')
    def test_run_existing_session_checks_concurrent_execution(
        self,
        mock_run,
        mock_process_manager_cls,
        agent
    ):
        """Test run_existing_session prevents concurrent execution."""
        # Mock process manager to indicate session is running
        mock_pm = Mock()
        mock_pm.is_running.return_value = True
        mock_process_manager_cls.return_value = mock_pm

        with pytest.raises(RuntimeError, match="Session test-session is already running"):
            agent.run_existing_session(
                session_id="test-session",
                instruction="Test"
            )

        mock_pm.is_running.assert_called_once_with("test-session")
        mock_run.assert_not_called()

    @patch('pipe.core.services.process_manager_service.ProcessManagerService')
    @patch('pipe.core.agents.takt_agent.subprocess.Popen')
    def test_run_existing_session_stream_registers_process(
        self,
        mock_popen,
        mock_process_manager_cls,
        agent
    ):
        """Test run_existing_session_stream registers process with manager."""
        # Mock process manager
        mock_pm = Mock()
        mock_pm.is_running.return_value = False
        mock_pm.register_process = Mock()
        mock_pm.cleanup_process = Mock()
        mock_process_manager_cls.return_value = mock_pm

        # Mock subprocess
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.stdout = iter([])
        mock_process.stderr.read.return_value = ""
        mock_process.stderr.close = Mock()
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        # Execute streaming
        list(agent.run_existing_session_stream(
            session_id="test-session",
            instruction="Test"
        ))

        # Verify process registration
        mock_pm.register_process.assert_called_once_with("test-session", 12345)
        mock_pm.cleanup_process.assert_called_once_with("test-session")

    @patch('pipe.core.services.process_manager_service.ProcessManagerService')
    @patch('pipe.core.agents.takt_agent.subprocess.Popen')
    def test_run_existing_session_stream_cleanup_on_error(
        self,
        mock_popen,
        mock_process_manager_cls,
        agent
    ):
        """Test run_existing_session_stream cleans up process on error."""
        # Mock process manager
        mock_pm = Mock()
        mock_pm.is_running.return_value = False
        mock_pm.register_process = Mock()
        mock_pm.cleanup_process = Mock()
        mock_process_manager_cls.return_value = mock_pm

        # Mock subprocess to raise error
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.stdout = None
        mock_popen.return_value = mock_process

        # Execute and expect cleanup even on error
        try:
            list(agent.run_existing_session_stream(
                session_id="test-session",
                instruction="Test"
            ))
        except Exception:
            pass

        # Verify cleanup was called
        mock_pm.cleanup_process.assert_called_once_with("test-session")
```

### Pattern 5: Search Agent Testing

Test grounding search integration.

```python
# tests/unit/core/agents/test_search_agent.py
import pytest
from unittest.mock import Mock, patch
from pipe.core.agents.search_agent import call_gemini_api_with_grounding
from pipe.core.models.settings import Settings


@pytest.fixture
def mock_settings():
    """Create mock Settings."""
    settings = Mock(spec=Settings)
    settings.search_model = Mock()
    settings.search_model.name = "gemini-2.0-flash-exp"
    settings.parameters = Mock()
    settings.parameters.temperature.value = 0.7
    settings.parameters.top_p.value = 0.9
    settings.parameters.top_k.value = 40
    return settings


class TestSearchAgent:
    """Test search agent grounding functionality."""

    @patch('pipe.core.agents.search_agent.genai.Client')
    def test_call_gemini_api_with_grounding_success(self, mock_client_cls, mock_settings):
        """Test successful grounding search API call."""
        # Mock API response
        mock_response = Mock()
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].content.parts = [Mock(text="Search result text")]

        mock_client = Mock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = call_gemini_api_with_grounding(
            settings=mock_settings,
            instruction="Search query",
            project_root="/tmp/test"
        )

        assert result == mock_response
        mock_client.models.generate_content.assert_called_once()

        # Verify Google Search tool was used
        call_kwargs = mock_client.models.generate_content.call_args[1]
        assert "config" in call_kwargs
        # Config should have tools with google_search

    def test_call_gemini_api_with_grounding_no_search_model(self, mock_settings):
        """Test raises ValueError when search_model not configured."""
        mock_settings.search_model = None

        with pytest.raises(ValueError, match="'search_model' not found"):
            call_gemini_api_with_grounding(
                settings=mock_settings,
                instruction="Query",
                project_root="/tmp/test"
            )

    @patch('pipe.core.agents.search_agent.genai.Client')
    def test_call_gemini_api_with_grounding_api_error(self, mock_client_cls, mock_settings):
        """Test error handling for API failures."""
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_client_cls.return_value = mock_client

        with pytest.raises(RuntimeError, match="Error during Gemini API execution"):
            call_gemini_api_with_grounding(
                settings=mock_settings,
                instruction="Query",
                project_root="/tmp/test"
            )
```

## Common Testing Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Testing Implementation Details

```python
# Bad: Testing internal method calls
def test_stream_content_calls_private_method(agent):
    with patch.object(agent, '_execute_streaming_call') as mock:
        agent.stream_content()
        mock.assert_called_once()  # Too coupled to implementation
```

### ❌ Anti-Pattern 2: Over-Mocking Domain Classes

```python
# Bad: Mocking domain classes that agents should delegate to
@patch('pipe.core.domains.gemini_api_payload.GeminiApiPayload')
def test_agent_without_integration(mock_payload_cls, agent):
    # This test loses value - we want to verify delegation works
    pass

# Better: Use real domain classes, mock only external calls
def test_agent_delegates_to_payload_service(agent):
    with patch.object(agent.payload_service, 'prepare_request') as mock_prepare:
        mock_prepare.return_value = ([], None)
        # Test delegation works with real payload service instance
```

### ❌ Anti-Pattern 3: Not Testing Return Value Structure

```python
# Bad: Not verifying return tuple structure
def test_run(agent):
    result = agent.run(args, session_service)
    assert result  # Too vague

# Good: Verify exact structure
def test_run_returns_correct_tuple(agent):
    response, token_count, turns, thought = agent.run(args, session_service)
    assert isinstance(response, str)
    assert isinstance(token_count, (int, type(None)))
    assert isinstance(turns, list)
    assert isinstance(thought, (str, type(None)))
```

## Summary

**Key Testing Principles for Agents Layer:**
- ✅ Test agent registry registration and lookup
- ✅ Verify delegation to domain classes (payload builders, stream processors)
- ✅ Verify delegation to delegates for complete workflows
- ✅ Mock external dependencies (API clients, subprocess)
- ✅ Test tool service integration with mocks
- ✅ Verify return value structure (tuple of 4 elements)
- ✅ Test subprocess management and process tracking
- ✅ Test error handling and propagation
- ❌ Don't test business logic (belongs in domains)
- ❌ Don't test workflow orchestration (belongs in delegates)
- ❌ Don't over-mock internal domain class delegation
- ❌ Don't test implementation details of private methods

**Agents are integration adapters - test integration points, not internal logic**
