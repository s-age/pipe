# CLI Layer Testing Strategy

**Layer:** `src/pipe/cli/`

## Responsibilities
- Command-line interface entry points (takt.py)
- Argument parsing and validation
- MCP (Model Context Protocol) server implementation (mcp_server.py)
- Language Server Protocol implementation (pygls_server.py)
- Tool discovery and schema generation
- JSON-RPC communication handling
- Environment setup and initialization

## Testing Strategy
- **Mock External Dependencies**: Mock subprocess calls, stdin/stdout, API clients
- **Focus**:
  - Argument parsing and validation
  - Command dispatching
  - MCP protocol compliance (JSON-RPC 2.0)
  - Tool discovery and schema generation
  - Service initialization
  - Error handling and user feedback
- **Testing Style**: Use fixtures for mock dependencies and integration tests for end-to-end CLI behavior

## CLI Characteristics
CLI modules are application entry points that:
- Handle user input from command-line arguments or stdin/stdout
- Parse and validate arguments using argparse
- Initialize services and coordinate with core layers
- Implement protocol specifications (MCP, LSP)
- Return exit codes and output to stdout/stderr
- Do NOT contain business logic (delegate to core layers)
- Do NOT contain data processing (delegate to domain/service layers)

## Test Patterns

### Pattern 1: Argument Parsing Testing (takt.py)

Test command-line argument parsing and validation.

```python
# tests/unit/cli/test_takt_argument_parsing.py
import pytest
from unittest.mock import patch, Mock
import sys
from io import StringIO


class TestTaktArgumentParsing:
    """Test command-line argument parsing for takt CLI."""

    def test_parse_new_session_arguments(self):
        """Test parsing arguments for creating a new session."""
        test_args = [
            'takt',
            '--purpose', 'Test purpose',
            '--background', 'Test background',
            '--instruction', 'Test instruction',
            '--roles', 'role1.yml',
            '--roles', 'role2.yml'
        ]

        with patch('sys.argv', test_args):
            from pipe.cli.takt import _parse_arguments
            args, parser = _parse_arguments()

            assert args.purpose == 'Test purpose'
            assert args.background == 'Test background'
            assert args.instruction == 'Test instruction'
            assert args.roles == ['role1.yml', 'role2.yml']

    def test_parse_existing_session_arguments(self):
        """Test parsing arguments for continuing an existing session."""
        test_args = [
            'takt',
            '--session', 'test-session-123',
            '--instruction', 'Follow-up instruction'
        ]

        with patch('sys.argv', test_args):
            from pipe.cli.takt import _parse_arguments
            args, parser = _parse_arguments()

            assert args.session == 'test-session-123'
            assert args.instruction == 'Follow-up instruction'

    def test_parse_fork_arguments(self):
        """Test parsing arguments for forking a session."""
        test_args = [
            'takt',
            '--fork', 'source-session-123',
            '--at-turn', '5',
            '--instruction', 'New instruction'
        ]

        with patch('sys.argv', test_args):
            from pipe.cli.takt import _parse_arguments
            args, parser = _parse_arguments()

            assert args.fork == 'source-session-123'
            assert args.at_turn == 5
            assert args.instruction == 'New instruction'

    def test_parse_output_format_arguments(self):
        """Test parsing output format arguments."""
        for format_type in ['json', 'text', 'stream-json']:
            test_args = [
                'takt',
                '--session', 'test-session',
                '--instruction', 'Test',
                '--output-format', format_type
            ]

            with patch('sys.argv', test_args):
                from pipe.cli.takt import _parse_arguments
                args, parser = _parse_arguments()

                assert args.output_format == format_type

    def test_parse_api_mode_argument(self):
        """Test parsing API mode argument."""
        test_args = [
            'takt',
            '--session', 'test-session',
            '--instruction', 'Test',
            '--api-mode', 'gemini-cli'
        ]

        with patch('sys.argv', test_args):
            from pipe.cli.takt import _parse_arguments
            args, parser = _parse_arguments()

            assert args.api_mode == 'gemini-cli'

    def test_parse_multi_step_reasoning_flag(self):
        """Test parsing multi-step reasoning flag."""
        test_args = [
            'takt',
            '--purpose', 'Test',
            '--background', 'Test',
            '--instruction', 'Test',
            '--multi-step-reasoning'
        ]

        with patch('sys.argv', test_args):
            from pipe.cli.takt import _parse_arguments
            args, parser = _parse_arguments()

            assert args.multi_step_reasoning is True

    def test_parse_multiple_references(self):
        """Test parsing multiple reference files."""
        test_args = [
            'takt',
            '--session', 'test-session',
            '--instruction', 'Test',
            '--references', 'ref1.md',
            '--references', 'ref2.md',
            '--references-persist', 'persist1.md'
        ]

        with patch('sys.argv', test_args):
            from pipe.cli.takt import _parse_arguments
            args, parser = _parse_arguments()

            assert args.references == ['ref1.md', 'ref2.md']
            assert args.references_persist == ['persist1.md']
```

### Pattern 2: Main Entry Point Testing

Test main function orchestration and error handling.

```python
# tests/unit/cli/test_takt_main.py
import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
from io import StringIO


class TestTaktMain:
    """Test main entry point for takt CLI."""

    @patch('pipe.cli.takt.check_and_show_warning')
    @patch('pipe.cli.takt.SettingsFactory.get_settings')
    @patch('pipe.cli.takt.ServiceFactory')
    @patch('pipe.cli.takt.dispatch')
    def test_main_success_new_session(
        self,
        mock_dispatch,
        mock_service_factory_cls,
        mock_get_settings,
        mock_check_warning
    ):
        """Test successful execution of main for new session."""
        # Setup mocks
        mock_check_warning.return_value = True
        mock_settings = Mock()
        mock_get_settings.return_value = mock_settings

        mock_service_factory = Mock()
        mock_session_service = Mock()
        mock_service_factory.create_session_service.return_value = mock_session_service
        mock_service_factory_cls.return_value = mock_service_factory

        test_args = [
            'takt',
            '--purpose', 'Test purpose',
            '--background', 'Test background',
            '--instruction', 'Test instruction'
        ]

        with patch('sys.argv', test_args):
            from pipe.cli.takt import main
            main()

        # Verify dispatch was called
        mock_dispatch.assert_called_once()
        call_args = mock_dispatch.call_args
        assert call_args[0][1] == mock_session_service

    @patch('pipe.cli.takt.check_and_show_warning')
    def test_main_warning_declined(self, mock_check_warning):
        """Test main exits when user declines warning."""
        mock_check_warning.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            from pipe.cli.takt import main
            main()

        assert exc_info.value.code == 1

    @patch('pipe.cli.takt.check_and_show_warning')
    @patch('pipe.cli.takt.SettingsFactory.get_settings')
    @patch('pipe.cli.takt.ServiceFactory')
    @patch('pipe.cli.takt.dispatch')
    def test_main_handles_value_error(
        self,
        mock_dispatch,
        mock_service_factory_cls,
        mock_get_settings,
        mock_check_warning
    ):
        """Test main handles ValueError from dispatch."""
        mock_check_warning.return_value = True
        mock_get_settings.return_value = Mock()

        mock_service_factory = Mock()
        mock_service_factory.create_session_service.return_value = Mock()
        mock_service_factory_cls.return_value = mock_service_factory

        # Mock dispatch to raise ValueError
        mock_dispatch.side_effect = ValueError("Test error")

        test_args = ['takt', '--session', 'test', '--instruction', 'Test']

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                from pipe.cli.takt import main
                main()

            assert exc_info.value.code == 1

    @patch('pipe.cli.takt.check_and_show_warning')
    @patch('pipe.cli.takt.SettingsFactory.get_settings')
    @patch('pipe.cli.takt.ServiceFactory')
    @patch('pipe.cli.takt.start_session_validator')
    def test_main_validates_new_session_args(
        self,
        mock_validator,
        mock_service_factory_cls,
        mock_get_settings,
        mock_check_warning
    ):
        """Test main validates arguments for new session."""
        mock_check_warning.return_value = True
        mock_get_settings.return_value = Mock()

        mock_service_factory = Mock()
        mock_service_factory.create_session_service.return_value = Mock()
        mock_service_factory_cls.return_value = mock_service_factory

        test_args = [
            'takt',
            '--purpose', 'Test purpose',
            '--instruction', 'Test instruction'
        ]

        with patch('sys.argv', test_args):
            with patch('pipe.cli.takt.dispatch'):
                from pipe.cli.takt import main
                main()

        # Verify validator was called
        mock_validator.validate.assert_called_once()
```

### Pattern 3: Warning Display Testing

Test user consent mechanism.

```python
# tests/unit/cli/test_takt_warning.py
import pytest
from unittest.mock import patch, mock_open, call
import os


class TestWarningDisplay:
    """Test warning display and user consent mechanism."""

    @patch('pipe.cli.takt.os.path.exists')
    def test_check_warning_when_already_unsealed(self, mock_exists):
        """Test check_and_show_warning when unsealed.txt exists."""
        def exists_side_effect(path):
            return path.endswith('unsealed.txt')

        mock_exists.side_effect = exists_side_effect

        from pipe.cli.takt import check_and_show_warning
        result = check_and_show_warning('/test/project')

        assert result is True

    @patch('pipe.cli.takt.read_text_file')
    @patch('pipe.cli.takt.os.path.exists')
    @patch('pipe.cli.takt.input')
    @patch('pipe.cli.takt.os.rename')
    def test_check_warning_user_agrees(
        self,
        mock_rename,
        mock_input,
        mock_exists,
        mock_read_text
    ):
        """Test check_and_show_warning when user agrees."""
        def exists_side_effect(path):
            return path.endswith('sealed.txt')

        mock_exists.side_effect = exists_side_effect
        mock_read_text.return_value = "Warning content"
        mock_input.return_value = "yes"

        from pipe.cli.takt import check_and_show_warning
        result = check_and_show_warning('/test/project')

        assert result is True
        mock_rename.assert_called_once()

    @patch('pipe.cli.takt.read_text_file')
    @patch('pipe.cli.takt.os.path.exists')
    @patch('pipe.cli.takt.input')
    def test_check_warning_user_declines(
        self,
        mock_input,
        mock_exists,
        mock_read_text
    ):
        """Test check_and_show_warning when user declines."""
        def exists_side_effect(path):
            return path.endswith('sealed.txt')

        mock_exists.side_effect = exists_side_effect
        mock_read_text.return_value = "Warning content"
        mock_input.return_value = "no"

        from pipe.cli.takt import check_and_show_warning
        result = check_and_show_warning('/test/project')

        assert result is False

    @patch('pipe.cli.takt.read_text_file')
    @patch('pipe.cli.takt.os.path.exists')
    @patch('pipe.cli.takt.input')
    def test_check_warning_invalid_then_valid_input(
        self,
        mock_input,
        mock_exists,
        mock_read_text
    ):
        """Test check_and_show_warning with invalid then valid input."""
        def exists_side_effect(path):
            return path.endswith('sealed.txt')

        mock_exists.side_effect = exists_side_effect
        mock_read_text.return_value = "Warning content"
        mock_input.side_effect = ["invalid", "maybe", "yes"]

        with patch('pipe.cli.takt.os.rename'):
            from pipe.cli.takt import check_and_show_warning
            result = check_and_show_warning('/test/project')

        assert result is True
        assert mock_input.call_count == 3
```

### Pattern 4: MCP Server Tool Discovery Testing

Test tool discovery and schema generation for MCP server.

```python
# tests/unit/cli/test_mcp_server_tool_discovery.py
import pytest
from unittest.mock import patch, Mock, MagicMock
import json


class TestMCPToolDiscovery:
    """Test MCP server tool discovery and schema generation."""

    @patch('pipe.cli.mcp_server.os.listdir')
    @patch('pipe.cli.mcp_server.os.path.isfile')
    @patch('pipe.cli.mcp_server.importlib.util.spec_from_file_location')
    @patch('pipe.cli.mcp_server.importlib.util.module_from_spec')
    def test_get_tool_definitions_discovers_tools(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_isfile,
        mock_listdir
    ):
        """Test get_tool_definitions discovers and parses tools."""
        # Mock filesystem
        mock_listdir.return_value = ['example_tool.py', '__init__.py']
        mock_isfile.return_value = True

        # Mock module loading
        mock_spec = Mock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = Mock()
        mock_module_from_spec.return_value = mock_module

        # Mock tool function
        def example_tool(arg1: str, arg2: int = 10) -> dict:
            """Example tool description.

            Args:
                arg1: First argument description
                arg2: Second argument description
            """
            return {}

        mock_module.example_tool = example_tool

        # Clear cache before test
        from pipe.cli.mcp_server import get_tool_definitions
        get_tool_definitions.cache_clear()

        with patch('pipe.cli.mcp_server.TOOLS_DIR', '/fake/tools'):
            with patch('pipe.cli.mcp_server.get_type_hints', return_value={
                'arg1': str,
                'arg2': int,
                'return': dict
            }):
                definitions = get_tool_definitions()

        # Verify tool was discovered
        assert len(definitions) > 0
        tool_def = definitions[0]
        assert tool_def['name'] == 'example_tool'
        assert 'description' in tool_def
        assert 'inputSchema' in tool_def

    def test_get_tool_definitions_caching(self):
        """Test that get_tool_definitions results are cached."""
        from pipe.cli.mcp_server import get_tool_definitions

        # Clear cache
        get_tool_definitions.cache_clear()

        with patch('pipe.cli.mcp_server.os.listdir', return_value=[]):
            first_call = get_tool_definitions()

            # Second call should not trigger os.listdir again
            with patch('pipe.cli.mcp_server.os.listdir') as mock_listdir:
                second_call = get_tool_definitions()
                mock_listdir.assert_not_called()

            assert first_call is second_call

    @patch('pipe.cli.mcp_server.get_type_hints')
    def test_tool_schema_type_mapping(self, mock_get_hints):
        """Test correct type mapping in tool schemas."""
        from pipe.cli.mcp_server import get_tool_definitions

        # Test type mappings
        type_tests = [
            (str, 'string'),
            (int, 'integer'),
            (float, 'number'),
            (bool, 'boolean'),
            (list, 'array'),
            (dict, 'object'),
        ]

        for python_type, json_type in type_tests:
            mock_get_hints.return_value = {
                'test_param': python_type,
                'return': dict
            }

            # Implementation depends on actual code structure
            # This is a conceptual test
```

### Pattern 5: MCP Server Tool Execution Testing

Test tool execution and result formatting.

```python
# tests/unit/cli/test_mcp_server_execution.py
import pytest
from unittest.mock import patch, Mock
import json


class TestMCPToolExecution:
    """Test MCP server tool execution."""

    @patch('pipe.cli.mcp_server.get_services')
    def test_execute_tool_success(self, mock_get_services):
        """Test successful tool execution."""
        # Setup mock services
        mock_settings = Mock()
        mock_session_service = Mock()
        mock_turn_service = Mock()
        mock_get_services.return_value = (
            mock_settings,
            mock_session_service,
            mock_turn_service
        )

        # Mock tool function
        def mock_tool(param1: str):
            return {"result": f"processed {param1}"}

        with patch('pipe.cli.mcp_server.importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.example_tool = mock_tool
            mock_import.return_value = mock_module

            from pipe.cli.mcp_server import execute_tool
            result = execute_tool('example_tool', {'param1': 'test'})

        assert 'result' in result
        assert result['result'] == 'processed test'

    @patch('pipe.cli.mcp_server.get_services')
    def test_execute_tool_with_error(self, mock_get_services):
        """Test tool execution with error."""
        mock_get_services.return_value = (Mock(), Mock(), Mock())

        # Mock tool function that raises error
        def failing_tool(param1: str):
            raise ValueError("Tool execution failed")

        with patch('pipe.cli.mcp_server.importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.failing_tool = failing_tool
            mock_import.return_value = mock_module

            from pipe.cli.mcp_server import execute_tool
            result = execute_tool('failing_tool', {'param1': 'test'})

        # Should return error information
        assert 'error' in result or result is None

    def test_format_mcp_tool_result_success(self):
        """Test formatting successful tool result."""
        from pipe.cli.mcp_server import format_mcp_tool_result

        result = {'data': 'test', 'status': 'success'}
        formatted = format_mcp_tool_result(result, is_error=False)

        assert 'content' in formatted
        assert isinstance(formatted['content'], list)

    def test_format_mcp_tool_result_error(self):
        """Test formatting error result."""
        from pipe.cli.mcp_server import format_mcp_tool_result

        error = "Something went wrong"
        formatted = format_mcp_tool_result(error, is_error=True)

        assert 'content' in formatted
        assert 'isError' in formatted
        assert formatted['isError'] is True
```

### Pattern 6: Service Initialization Testing

Test service initialization and caching.

```python
# tests/unit/cli/test_mcp_server_initialization.py
import pytest
from unittest.mock import patch, Mock


class TestServiceInitialization:
    """Test MCP server service initialization."""

    @patch('pipe.cli.mcp_server.SettingsRepository')
    @patch('pipe.cli.mcp_server.ServiceFactory')
    def test_initialize_services_creates_all_services(
        self,
        mock_factory_cls,
        mock_repo_cls
    ):
        """Test initialize_services creates all required services."""
        # Setup mocks
        mock_repo = Mock()
        mock_settings = Mock()
        mock_repo.load.return_value = mock_settings
        mock_repo_cls.return_value = mock_repo

        mock_factory = Mock()
        mock_session_service = Mock()
        mock_turn_service = Mock()
        mock_factory.create_session_service.return_value = mock_session_service
        mock_factory.create_session_turn_service.return_value = mock_turn_service
        mock_factory_cls.return_value = mock_factory

        # Reset global state
        import pipe.cli.mcp_server as mcp
        mcp._SETTINGS = None
        mcp._SERVICE_FACTORY = None
        mcp._SESSION_SERVICE = None
        mcp._SESSION_TURN_SERVICE = None

        from pipe.cli.mcp_server import initialize_services
        initialize_services()

        # Verify all services were created
        mock_repo_cls.assert_called_once()
        mock_factory_cls.assert_called_once()
        mock_factory.create_session_service.assert_called_once()
        mock_factory.create_session_turn_service.assert_called_once()

    def test_get_services_initializes_if_needed(self):
        """Test get_services initializes services if not already done."""
        # Reset global state
        import pipe.cli.mcp_server as mcp
        mcp._SETTINGS = None

        with patch('pipe.cli.mcp_server.initialize_services') as mock_init:
            from pipe.cli.mcp_server import get_services
            get_services()

            mock_init.assert_called_once()

    def test_get_services_returns_cached_services(self):
        """Test get_services returns cached services."""
        import pipe.cli.mcp_server as mcp

        # Set up cached services
        mock_settings = Mock()
        mock_session_service = Mock()
        mock_turn_service = Mock()

        mcp._SETTINGS = mock_settings
        mcp._SESSION_SERVICE = mock_session_service
        mcp._SESSION_TURN_SERVICE = mock_turn_service

        from pipe.cli.mcp_server import get_services
        settings, session_svc, turn_svc = get_services()

        assert settings is mock_settings
        assert session_svc is mock_session_service
        assert turn_svc is mock_turn_service
```

## Common Testing Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Testing Implementation Details

```python
# Bad: Testing internal parsing logic
def test_argument_parser_internals(parser):
    assert hasattr(parser, '_actions')
    assert len(parser._actions) > 0  # Too coupled to argparse internals
```

### ❌ Anti-Pattern 2: Not Mocking External I/O

```python
# Bad: Testing with actual stdin/stdout
def test_main_output():
    main()  # Writes to actual stdout, depends on terminal state

# Good: Mock stdout for testing
def test_main_output():
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        main()
        output = mock_stdout.getvalue()
        assert "Expected output" in output
```

### ❌ Anti-Pattern 3: Over-Testing JSON-RPC Protocol Details

```python
# Bad: Testing JSON-RPC format details (should be handled by library)
def test_jsonrpc_format():
    response = {"jsonrpc": "2.0", "id": 1, "result": {}}
    assert response["jsonrpc"] == "2.0"  # Library's responsibility

# Good: Test application-specific protocol behavior
def test_tool_call_response_structure():
    result = execute_tool('tool_name', {'arg': 'value'})
    assert 'content' in result
    assert isinstance(result['content'], list)
```

## Summary

**Key Testing Principles for CLI Layer:**
- ✅ Test argument parsing with various combinations
- ✅ Test main entry point orchestration
- ✅ Mock external I/O (stdin, stdout, subprocess)
- ✅ Test tool discovery and schema generation
- ✅ Test MCP protocol compliance (tool execution, result formatting)
- ✅ Test service initialization and caching
- ✅ Test error handling and user feedback
- ✅ Test exit codes and error messages
- ❌ Don't test business logic (belongs in core layers)
- ❌ Don't test protocol format details (library's responsibility)
- ❌ Don't use actual file I/O or subprocess execution
- ❌ Don't test implementation details of third-party libraries

**CLI modules are thin orchestration layers - test coordination and I/O handling, not domain logic**
