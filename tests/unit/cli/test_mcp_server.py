"""Unit tests for the MCP server implementation."""

import json
from unittest.mock import MagicMock, patch

import pytest
from pipe.cli.mcp_server import (
    execute_tool,
    format_mcp_tool_result,
    get_latest_session_id,
    get_services,
    get_tool_definitions,
    initialize_services,
    main,
    prepare_tool_arguments,
)
from pydantic import BaseModel


class TestServiceInitialization:
    """Tests for service initialization and retrieval."""

    @patch("pipe.cli.mcp_server.SettingsRepository")
    @patch("pipe.cli.mcp_server.ServiceFactory")
    def test_initialize_services(self, mock_factory_class, mock_repo_class):
        """Test that services are initialized correctly."""
        # Reset global state
        import pipe.cli.mcp_server as mcp

        mcp._SETTINGS = None
        mcp._SERVICE_FACTORY = None
        mcp._SESSION_SERVICE = None
        mcp._SESSION_TURN_SERVICE = None

        mock_repo = mock_repo_class.return_value
        mock_settings = MagicMock()
        mock_repo.load.return_value = mock_settings

        mock_factory = mock_factory_class.return_value
        mock_session_service = MagicMock()
        mock_turn_service = MagicMock()
        mock_factory.create_session_service.return_value = mock_session_service
        mock_factory.create_session_turn_service.return_value = mock_turn_service

        initialize_services()

        assert mcp._SETTINGS == mock_settings
        assert mcp._SERVICE_FACTORY == mock_factory
        assert mcp._SESSION_SERVICE == mock_session_service
        assert mcp._SESSION_TURN_SERVICE == mock_turn_service

        mock_repo.load.assert_called_once()
        mock_factory_class.assert_called_once_with(mcp.BASE_DIR, mock_settings)
        mock_factory.create_session_service.assert_called_once()
        mock_factory.create_session_turn_service.assert_called_once()

    @patch("pipe.cli.mcp_server.initialize_services")
    def test_get_services_initializes_if_none(self, mock_init):
        """Test that get_services calls initialize_services if _SETTINGS is None."""
        import pipe.cli.mcp_server as mcp

        mcp._SETTINGS = None

        # Mock initialize_services to set the global variables
        def side_effect():
            mcp._SETTINGS = MagicMock()
            mcp._SESSION_SERVICE = MagicMock()
            mcp._SESSION_TURN_SERVICE = MagicMock()

        mock_init.side_effect = side_effect

        settings, session_svc, turn_svc = get_services()

        mock_init.assert_called_once()
        assert settings == mcp._SETTINGS
        assert session_svc == mcp._SESSION_SERVICE
        assert turn_svc == mcp._SESSION_TURN_SERVICE

    def test_get_services_returns_cached(self):
        """Test that get_services returns cached services if already initialized."""
        import pipe.cli.mcp_server as mcp

        mcp._SETTINGS = MagicMock()
        mcp._SESSION_SERVICE = MagicMock()
        mcp._SESSION_TURN_SERVICE = MagicMock()

        with patch("pipe.cli.mcp_server.initialize_services") as mock_init:
            settings, session_svc, turn_svc = get_services()
            mock_init.assert_not_called()
            assert settings == mcp._SETTINGS
            assert session_svc == mcp._SESSION_SERVICE
            assert turn_svc == mcp._SESSION_TURN_SERVICE


class TestToolDiscovery:
    """Tests for tool discovery and schema generation."""

    @patch("pipe.cli.mcp_server.os.listdir")
    @patch("pipe.cli.mcp_server.importlib.util.spec_from_file_location")
    @patch("pipe.cli.mcp_server.importlib.util.module_from_spec")
    @patch("pipe.cli.mcp_server.get_type_hints")
    def test_get_tool_definitions_success(
        self, mock_get_hints, mock_module_from_spec, mock_spec_from_file, mock_listdir
    ):
        """Test successful tool discovery and schema generation."""
        get_tool_definitions.cache_clear()
        mock_listdir.return_value = ["test_tool.py", "__init__.py", "not_a_tool.txt"]

        mock_spec = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        class MockBaseModel(BaseModel):
            field: str

        def test_tool(
            arg1: str,
            arg2: int = 10,
            arg3: list[str] | None = None,
            arg4: MockBaseModel | None = None,
        ):
            """Test tool description."""
            return {}

        mock_module.test_tool = test_tool
        mock_get_hints.return_value = {
            "arg1": str,
            "arg2": int,
            "arg3": list[str],
            "arg4": MockBaseModel,
        }

        with patch("pipe.cli.mcp_server.TOOLS_DIR", "/fake/tools"):
            tool_defs = get_tool_definitions()

        assert len(tool_defs) == 1
        tool_def = tool_defs[0]
        assert tool_def["name"] == "test_tool"
        assert tool_def["description"] == "Test tool description."
        assert "arg1" in tool_def["inputSchema"]["properties"]
        assert "arg2" in tool_def["inputSchema"]["properties"]
        assert "arg3" in tool_def["inputSchema"]["properties"]
        assert "arg4" in tool_def["inputSchema"]["properties"]
        assert "arg1" in tool_def["inputSchema"]["required"]
        assert "arg2" not in tool_def["inputSchema"]["required"]

    @patch("pipe.cli.mcp_server.os.listdir")
    def test_get_tool_definitions_empty(self, mock_listdir):
        """Test tool discovery when no tools are found."""
        get_tool_definitions.cache_clear()
        mock_listdir.return_value = []
        tool_defs = get_tool_definitions()
        assert tool_defs == []

    @patch("pipe.cli.mcp_server.os.listdir")
    def test_get_tool_definitions_error(self, mock_listdir):
        """Test tool discovery when an error occurs during listdir."""
        get_tool_definitions.cache_clear()
        mock_listdir.side_effect = Exception("OS error")
        tool_defs = get_tool_definitions()
        assert tool_defs == []

    @patch("pipe.cli.mcp_server.os.listdir")
    @patch("pipe.cli.mcp_server.importlib.util.spec_from_file_location")
    @patch("pipe.cli.mcp_server.importlib.util.module_from_spec")
    @patch("pipe.cli.mcp_server.get_type_hints")
    @patch("pipe.cli.mcp_server.inspect.isclass")
    def test_get_tool_definitions_with_dict_type(
        self,
        mock_isclass,
        mock_get_hints,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
    ):
        """Test tool discovery with dict type parameters."""
        get_tool_definitions.cache_clear()
        mock_listdir.return_value = ["dict_tool.py"]

        mock_spec = MagicMock()
        mock_spec_from_file.return_value = mock_spec
        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        # Mock dict type to have __origin__ = dict
        mock_dict_type = MagicMock()
        mock_dict_type.__origin__ = dict

        def dict_tool(data: dict, optional_dict: dict | None = None):
            """Tool with dict parameters."""
            return {}

        mock_module.dict_tool = dict_tool
        mock_get_hints.return_value = {
            "data": mock_dict_type,
            "optional_dict": mock_dict_type,
        }
        mock_isclass.return_value = False

        with patch("pipe.cli.mcp_server.TOOLS_DIR", "/fake/tools"):
            tool_defs = get_tool_definitions()

        assert len(tool_defs) == 1
        tool_def = tool_defs[0]
        assert tool_def["inputSchema"]["properties"]["data"]["type"] == "object"
        assert (
            tool_def["inputSchema"]["properties"]["optional_dict"]["type"] == "object"
        )
        assert "data" in tool_def["inputSchema"]["required"]
        assert "optional_dict" not in tool_def["inputSchema"]["required"]

    @patch("pipe.cli.mcp_server.os.listdir")
    @patch("pipe.cli.mcp_server.importlib.util.spec_from_file_location")
    @patch("pipe.cli.mcp_server.importlib.util.module_from_spec")
    @patch("pipe.cli.mcp_server.get_type_hints")
    def test_get_tool_definitions_with_list_of_dicts(
        self, mock_get_hints, mock_module_from_spec, mock_spec_from_file, mock_listdir
    ):
        """Test tool discovery with list of dicts."""
        get_tool_definitions.cache_clear()
        mock_listdir.return_value = ["list_tool.py"]

        mock_spec = MagicMock()
        mock_spec_from_file.return_value = mock_spec
        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        def list_tool(items: list[dict]):
            """Tool with list of dicts."""
            return {}

        mock_module.list_tool = list_tool
        mock_get_hints.return_value = {"items": list[dict]}

        with patch("pipe.cli.mcp_server.TOOLS_DIR", "/fake/tools"):
            tool_defs = get_tool_definitions()

        assert len(tool_defs) == 1
        tool_def = tool_defs[0]
        assert tool_def["inputSchema"]["properties"]["items"]["type"] == "array"
        assert (
            tool_def["inputSchema"]["properties"]["items"]["items"]["type"] == "object"
        )

    @patch("pipe.cli.mcp_server.os.listdir")
    @patch("pipe.cli.mcp_server.importlib.util.spec_from_file_location")
    @patch("pipe.cli.mcp_server.importlib.util.module_from_spec")
    @patch("pipe.cli.mcp_server.get_type_hints")
    @patch("pipe.cli.mcp_server.inspect.isclass")
    def test_get_tool_definitions_with_union_types(
        self,
        mock_isclass,
        mock_get_hints,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
    ):
        """Test tool discovery with Union types in list items."""
        get_tool_definitions.cache_clear()
        mock_listdir.return_value = ["union_tool.py"]

        mock_spec = MagicMock()
        mock_spec_from_file.return_value = mock_spec
        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        def union_tool(mixed_items: list[dict | str]):
            """Tool with union type in list."""
            return {}

        mock_module.union_tool = union_tool
        # Create mock list type with Union item type
        from typing import Union

        mock_list_type = MagicMock()
        mock_list_type.__origin__ = list

        # Mock the Union type for list items
        mock_union_item = MagicMock()
        mock_union_item.__origin__ = Union

        # Create mock dict with __origin__ = dict
        mock_dict = MagicMock()
        mock_dict.__origin__ = dict

        # Mock get_args to return the union args
        with patch("pipe.cli.mcp_server.get_args") as mock_get_args:
            # First call: get_args on list returns [Union[dict, str]]
            # Second call: get_args on Union returns (dict, str)
            mock_get_args.side_effect = [
                [mock_union_item],  # list item type
                [mock_dict, str],  # union args
            ]

            mock_get_hints.return_value = {"mixed_items": mock_list_type}
            mock_isclass.return_value = False

            with patch("pipe.cli.mcp_server.TOOLS_DIR", "/fake/tools"):
                tool_defs = get_tool_definitions()

        assert len(tool_defs) == 1
        tool_def = tool_defs[0]
        assert tool_def["inputSchema"]["properties"]["mixed_items"]["type"] == "array"
        assert (
            tool_def["inputSchema"]["properties"]["mixed_items"]["items"]["type"]
            == "object"
        )

    @patch("pipe.cli.mcp_server.os.listdir")
    @patch("pipe.cli.mcp_server.importlib.util.spec_from_file_location")
    @patch("pipe.cli.mcp_server.importlib.util.module_from_spec")
    @patch("pipe.cli.mcp_server.get_type_hints")
    def test_get_tool_definitions_skips_server_args(
        self, mock_get_hints, mock_module_from_spec, mock_spec_from_file, mock_listdir
    ):
        """Test that server-side arguments are excluded from schema."""
        get_tool_definitions.cache_clear()
        mock_listdir.return_value = ["server_tool.py"]

        mock_spec = MagicMock()
        mock_spec_from_file.return_value = mock_spec
        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        def server_tool(
            user_arg: str,
            session_service=None,
            session_id=None,
            settings=None,
            project_root=None,
        ):
            """Tool with server arguments."""
            return {}

        mock_module.server_tool = server_tool
        mock_get_hints.return_value = {
            "user_arg": str,
            "session_service": object,
            "session_id": str,
            "settings": object,
            "project_root": str,
        }

        with patch("pipe.cli.mcp_server.TOOLS_DIR", "/fake/tools"):
            tool_defs = get_tool_definitions()

        assert len(tool_defs) == 1
        tool_def = tool_defs[0]
        # Only user_arg should be in the schema
        assert "user_arg" in tool_def["inputSchema"]["properties"]
        assert "session_service" not in tool_def["inputSchema"]["properties"]
        assert "session_id" not in tool_def["inputSchema"]["properties"]
        assert "settings" not in tool_def["inputSchema"]["properties"]
        assert "project_root" not in tool_def["inputSchema"]["properties"]


class TestSessionId:
    """Tests for session ID retrieval."""

    def test_get_latest_session_id_from_env(self, monkeypatch):
        """Test getting session ID from environment variable."""
        monkeypatch.setenv("PIPE_SESSION_ID", "test-session-123")
        assert get_latest_session_id() == "test-session-123"

    def test_get_latest_session_id_none(self, monkeypatch):
        """Test getting session ID when environment variable is not set."""
        monkeypatch.delenv("PIPE_SESSION_ID", raising=False)
        assert get_latest_session_id() is None


class TestToolExecution:
    """Tests for tool execution."""

    @patch("pipe.cli.mcp_server.get_services")
    @patch("pipe.cli.mcp_server.get_latest_session_id")
    @patch("pipe.cli.mcp_server.importlib.util.spec_from_file_location")
    @patch("pipe.cli.mcp_server.importlib.util.module_from_spec")
    @patch("pipe.cli.mcp_server.StreamingLogRepository")
    @patch("pipe.cli.mcp_server.get_current_timestamp")
    def test_execute_tool_success(
        self,
        mock_get_ts,
        mock_log_repo_class,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_get_session_id,
        mock_get_services,
    ):
        """Test successful tool execution with logging."""
        mock_settings = MagicMock()
        mock_session_svc = MagicMock()
        mock_turn_svc = MagicMock()
        mock_get_services.return_value = (
            mock_settings,
            mock_session_svc,
            mock_turn_svc,
        )
        mock_get_session_id.return_value = "test-session"
        mock_get_ts.return_value = "2026-01-01T00:00:00Z"

        mock_spec = MagicMock()
        mock_spec_from_file.return_value = mock_spec
        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        def test_tool(arg1):
            return {"data": f"result-{arg1}", "error": None}

        mock_module.test_tool = test_tool

        with patch("pipe.cli.mcp_server.os.path.exists", return_value=True):
            result = execute_tool("test_tool", {"arg1": "val1"})

        assert result == {"data": "result-val1", "error": None}
        mock_turn_svc.add_to_pool.assert_called()
        assert (
            mock_turn_svc.add_to_pool.call_count == 2
        )  # FunctionCalling and ToolResponse

    @patch("pipe.cli.mcp_server.get_services")
    def test_execute_tool_invalid_name(self, mock_get_services):
        """Test that invalid tool names raise ValueError."""
        mock_get_services.return_value = (MagicMock(), MagicMock(), MagicMock())
        with pytest.raises(ValueError, match="Invalid tool name."):
            execute_tool("../secret", {})

    @patch("pipe.cli.mcp_server.get_services")
    def test_execute_tool_not_found(self, mock_get_services):
        """Test that missing tool files raise FileNotFoundError."""
        mock_get_services.return_value = (MagicMock(), MagicMock(), MagicMock())
        with patch("pipe.cli.mcp_server.os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Tool 'missing' not found."):
                execute_tool("missing", {})


class TestArgumentPreparation:
    """Tests for tool argument preparation."""

    def test_prepare_tool_arguments_injection(self):
        """Test that server-side dependencies are injected correctly."""

        def tool_func(session_service, session_id, settings, project_root, user_arg):
            pass

        client_args = {"user_arg": "val"}
        session_svc = MagicMock()
        session_id = "test-id"
        settings = MagicMock()
        project_root = "/root"

        final_args = prepare_tool_arguments(
            tool_func, client_args, session_svc, session_id, settings, project_root
        )

        assert final_args["session_service"] == session_svc
        assert final_args["session_id"] == session_id
        assert final_args["settings"] == settings
        assert final_args["project_root"] == project_root
        assert final_args["user_arg"] == "val"

    def test_prepare_tool_arguments_no_injection(self):
        """Test that arguments are not injected if not in signature."""

        def tool_func(user_arg):
            pass

        client_args = {"user_arg": "val"}
        final_args = prepare_tool_arguments(
            tool_func, client_args, MagicMock(), "id", MagicMock(), "/root"
        )

        assert final_args == {"user_arg": "val"}


class TestResultFormatting:
    """Tests for MCP result formatting."""

    def test_format_mcp_tool_result_string(self):
        """Test formatting a string result."""
        result = format_mcp_tool_result("success", is_error=False)
        assert result == {
            "content": [{"type": "text", "text": "success"}],
            "isError": False,
        }

    def test_format_mcp_tool_result_dict(self):
        """Test formatting a dictionary result."""
        data = {"key": "value"}
        result = format_mcp_tool_result(data, is_error=True)
        assert result == {
            "content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}],
            "isError": True,
        }


class TestMainLoop:
    """Tests for the main stdio loop."""

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    @patch("pipe.cli.mcp_server.get_tool_definitions")
    def test_main_initialize(self, mock_get_defs, mock_select, mock_stdout, mock_stdin):
        """Test the 'initialize' method in the main loop."""
        # First call returns stdin ready, second call returns empty to break the loop
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {"protocolVersion": "2025-06-18"},
                }
            ),
            "",  # Empty string to signal stdin closed
        ]
        mock_get_defs.return_value = [{"name": "test"}]

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 1
        assert response["result"]["serverInfo"]["name"] == "pipe_mcp_server"
        assert response["result"]["tools"] == [{"name": "test"}]

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    def test_main_ping(self, mock_select, mock_stdout, mock_stdin):
        """Test the 'ping' method in the main loop."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"}),
            "",  # Empty string to signal stdin closed
        ]

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 2
        assert response["result"] == {}

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    @patch("pipe.cli.mcp_server.execute_tool")
    def test_main_tools_call_success(
        self, mock_execute, mock_select, mock_stdout, mock_stdin
    ):
        """Test the 'tools/call' method in the main loop."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "test_tool", "args": {"a": 1}},
                }
            ),
            "",  # Empty string to signal stdin closed
        ]
        mock_execute.return_value = {"data": "ok", "error": None}

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 3
        assert "ok" in response["result"]["content"][0]["text"]

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    @patch("pipe.cli.mcp_server.execute_tool")
    def test_main_tools_call_error(
        self, mock_execute, mock_select, mock_stdout, mock_stdin
    ):
        """Test the 'tools/call' method with an error in the main loop."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {"name": "fail_tool", "args": {}},
                }
            ),
            "",  # Empty string to signal stdin closed
        ]
        mock_execute.side_effect = Exception("Tool failed")

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 4
        assert response["result"]["isError"] is True
        assert "Tool failed" in response["result"]["content"][0]["text"]

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    @patch("pipe.cli.mcp_server.get_tool_definitions")
    def test_main_tools_list(self, mock_get_defs, mock_select, mock_stdout, mock_stdin):
        """Test the 'tools/list' method in the main loop."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps({"jsonrpc": "2.0", "id": 5, "method": "tools/list"}),
            "",
        ]
        mock_get_defs.return_value = [
            {"name": "tool1", "description": "First tool"},
            {"name": "tool2", "description": "Second tool"},
        ]

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 5
        assert len(response["result"]["tools"]) == 2
        assert response["result"]["tools"][0]["name"] == "tool1"
        assert response["result"]["prompts"] == []

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    def test_main_notifications_initialized(self, mock_select, mock_stdout, mock_stdin):
        """Test the 'notifications/initialized' method (no response expected)."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps(
                {"jsonrpc": "2.0", "method": "notifications/initialized"}
            ),  # No id for notification
            "",
        ]

        main()

        # Notifications should not produce a response
        assert mock_stdout.write.call_count == 0

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    def test_main_method_not_found(self, mock_select, mock_stdout, mock_stdin):
        """Test that unknown methods return a method not found error."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps({"jsonrpc": "2.0", "id": 6, "method": "unknown/method"}),
            "",
        ]

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 6
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    @patch("pipe.cli.mcp_server.execute_tool")
    def test_main_run_tool_success(
        self, mock_execute, mock_select, mock_stdout, mock_stdin
    ):
        """Test the 'run_tool' method with success."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "run_tool",
                    "params": {"tool_name": "test_tool", "arguments": {"x": 1}},
                }
            ),
            "",
        ]
        mock_execute.return_value = {"data": {"value": 42}, "error": None}

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 7
        assert response["result"]["status"] == "succeeded"
        assert response["result"]["result"]["value"] == 42

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    @patch("pipe.cli.mcp_server.execute_tool")
    def test_main_run_tool_error(
        self, mock_execute, mock_select, mock_stdout, mock_stdin
    ):
        """Test the 'run_tool' method with tool error."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 8,
                    "method": "run_tool",
                    "params": {"tool_name": "bad_tool", "arguments": {}},
                }
            ),
            "",
        ]
        mock_execute.return_value = {"error": "Tool execution failed"}

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 8
        assert "error" in response
        assert response["error"]["code"] == -32000
        assert "failed" in response["error"]["message"]

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    @patch("pipe.cli.mcp_server.execute_tool")
    def test_main_run_tool_exception(
        self, mock_execute, mock_select, mock_stdout, mock_stdin
    ):
        """Test the 'run_tool' method with exception."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 9,
                    "method": "run_tool",
                    "params": {"tool_name": "crash_tool", "arguments": {}},
                }
            ),
            "",
        ]
        mock_execute.side_effect = Exception("Unexpected error")

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 9
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Unexpected error" in response["error"]["message"]

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    def test_main_invalid_json(self, mock_select, mock_stdout, mock_stdin):
        """Test that invalid JSON is ignored gracefully."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            "not valid json{{{",
            "",
        ]

        main()

        # Should not crash, and no response should be written
        assert mock_stdout.write.call_count == 0

    @patch("pipe.cli.mcp_server.sys.stdin")
    @patch("pipe.cli.mcp_server.sys.stdout")
    @patch("pipe.cli.mcp_server.select.select")
    @patch("pipe.cli.mcp_server.execute_tool")
    def test_main_tools_call_with_arguments_param(
        self, mock_execute, mock_select, mock_stdout, mock_stdin
    ):
        """Test the 'tools/call' method using 'arguments' instead of 'args'."""
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]
        mock_stdin.readline.side_effect = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 10,
                    "method": "tools/call",
                    "params": {"name": "test_tool", "arguments": {"y": 2}},
                }
            ),
            "",
        ]
        mock_execute.return_value = {"data": "result", "error": None}

        main()

        output = mock_stdout.write.call_args[0][0]
        response = json.loads(output)
        assert response["id"] == 10
        mock_execute.assert_called_once_with("test_tool", {"y": 2})
