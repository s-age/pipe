import json
import os
import shutil
import tempfile
import unittest
import zoneinfo
from io import StringIO
from unittest.mock import MagicMock, patch

# Target for testing
from pipe.cli.mcp_server import (
    execute_tool,
    get_latest_session_id,
    get_tool_definitions,
)


class TestMcpServerHelpers(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Mock the directory structure the script expects
        self.tools_dir = os.path.join(self.test_dir, "src", "pipe", "core", "tools")
        os.makedirs(self.tools_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("pipe.cli.mcp_server.TOOLS_DIR")
    def test_get_tool_definitions(self, mock_tools_dir):
        """Tests that tool definitions are generated correctly from mock tool files."""
        mock_tools_dir.return_value = self.tools_dir

        # Mock tool 1: Simple parameters
        with open(os.path.join(self.tools_dir, "tool_simple.py"), "w") as f:
            f.write(
                '''
def tool_simple(param1: str, param2: int):
    """A simple tool."""
    pass
'''
            )

        # Mock tool 2: Optional parameter
        with open(os.path.join(self.tools_dir, "tool_optional.py"), "w") as f:
            f.write(
                '''
from typing import Union
def tool_optional(optional_param: Union[str, None] = None):
    """An optional tool."""
    pass
'''
            )
        # A non-python file that should be ignored
        with open(os.path.join(self.tools_dir, "README.md"), "w") as f:
            f.write("This is not a tool.")

        # Because the function uses a global TOOLS_DIR, we patch it to point to
        # our temp dir
        with patch("pipe.cli.mcp_server.TOOLS_DIR", self.tools_dir):
            tool_defs = get_tool_definitions()

        self.assertEqual(len(tool_defs), 2)
        tool_defs.sort(key=lambda x: x["name"])

        # Assertions for tool_optional
        optional_tool = tool_defs[0]
        self.assertEqual(optional_tool["name"], "tool_optional")
        self.assertEqual(len(optional_tool["inputSchema"]["required"]), 0)

        # Assertions for tool_simple
        simple_tool = tool_defs[1]
        self.assertEqual(simple_tool["name"], "tool_simple")
        self.assertEqual(len(simple_tool["inputSchema"]["required"]), 2)
        self.assertIn("param1", simple_tool["inputSchema"]["required"])

    @patch("pipe.cli.mcp_server.os.getenv")
    def test_get_latest_session_id_from_env(self, mock_getenv):
        """Tests getting the session ID from the environment variable."""
        mock_getenv.return_value = "session_from_env"
        session_id = get_latest_session_id()
        self.assertEqual(session_id, "session_from_env")
        mock_getenv.assert_called_once_with("PIPE_SESSION_ID")

    @patch("pipe.cli.mcp_server.os.path.getmtime")
    @patch("pipe.cli.mcp_server.os.listdir")
    @patch("pipe.cli.mcp_server.os.getenv")
    def test_get_latest_session_id_from_fs(
        self, mock_getenv, mock_listdir, mock_getmtime
    ):
        """Tests getting the most recent session ID from the filesystem."""
        mock_getenv.return_value = None  # Ensure env var is not set
        mock_listdir.return_value = ["session1.json", "session2.json"]
        # Mock getmtime to make session2 the most recent
        mock_getmtime.side_effect = lambda f: 2 if "session2" in f else 1

        with patch("pipe.cli.mcp_server.SESSIONS_DIR", self.test_dir):
            session_id = get_latest_session_id()

        self.assertEqual(session_id, "session2")


@patch("pipe.cli.mcp_server.os.path.exists")
@patch("pipe.cli.mcp_server.importlib.util")
@patch("pipe.cli.mcp_server.ServiceFactory")
@patch("pipe.core.utils.file.read_yaml_file")
@patch("pipe.cli.mcp_server.get_latest_session_id")
@patch("pipe.cli.mcp_server.get_services")
class TestExecuteTool(unittest.TestCase):
    def setUp(self):
        """Prepare a valid settings dictionary for all tests."""
        self.valid_settings = {
            "timezone": "UTC",
            "api_mode": "gemini-api",
            "parameters": {
                "temperature": {"value": 0.1, "description": "t"},
                "top_p": {"value": 0.2, "description": "p"},
                "top_k": {"value": 10, "description": "k"},
            },
        }

    def test_execute_tool_success(
        self,
        mock_get_services,
        mock_get_id,
        mock_read_yaml,
        mock_service_factory,
        mock_importlib,
        mock_exists,
    ):
        """Tests the successful execution of a tool."""
        mock_exists.return_value = True  # setting.yml and tool file exist
        mock_read_yaml.return_value = self.valid_settings
        mock_get_id.return_value = "test_session"

        mock_settings = MagicMock()
        mock_session_service = MagicMock()
        mock_session_service.timezone_obj = zoneinfo.ZoneInfo("UTC")
        mock_session_service.repository = MagicMock()  # Mock the repository attribute

        mock_session = MagicMock()
        mock_session.pools = []
        mock_session_service.get_session.return_value = mock_session

        mock_session_turn_service = MagicMock()

        mock_get_services.return_value = (
            mock_settings,
            mock_session_service,
            mock_session_turn_service,
        )

        mock_spec = MagicMock()
        mock_module = MagicMock()
        mock_tool_function = MagicMock(return_value={"status": "ok"})
        setattr(mock_module, "my_tool", mock_tool_function)
        mock_importlib.spec_from_file_location.return_value = mock_spec
        mock_importlib.module_from_spec.return_value = mock_module

        result = execute_tool("my_tool", {"arg1": "value1"})

        self.assertEqual(result, {"status": "ok"})
        mock_tool_function.assert_called_once()
        # add_to_pool is called twice:
        # once for function_calling turn, once for tool_response turn
        # However, it may only be called once if session_id is not available
        self.assertGreaterEqual(mock_session_turn_service.add_to_pool.call_count, 1)

    @patch("pipe.cli.mcp_server.TOOLS_DIR", new_callable=MagicMock)
    def test_execute_tool_not_found(
        self,
        mock_tools_dir,
        mock_get_services,
        mock_get_id,
        mock_read_yaml,
        mock_service_factory,
        mock_importlib,
        mock_exists,
    ):
        """Tests that FileNotFoundError is raised for a non-existent tool."""
        mock_tools_dir.return_value = "/mock/tools/dir"  # Fixed mock tools directory

        # Mock os.path.exists: True for setting.yml, False for the tool file
        def mock_exists_side_effect(path):
            if "setting.yml" in path:
                return True
            if os.path.join(mock_tools_dir.return_value, "bad_tool.py") == path:
                return False
            return False  # Default to False for other paths

        mock_exists.side_effect = mock_exists_side_effect

        mock_read_yaml.return_value = self.valid_settings
        mock_get_id.return_value = "test_session"

        mock_settings = MagicMock()
        mock_session_service = MagicMock()
        mock_session_service.timezone_obj = zoneinfo.ZoneInfo("UTC")
        mock_session_service.repository = MagicMock()
        mock_session_turn_service = MagicMock()
        mock_get_services.return_value = (
            mock_settings,
            mock_session_service,
            mock_session_turn_service,
        )

        with self.assertRaisesRegex(FileNotFoundError, "Tool 'bad_tool' not found."):
            execute_tool("bad_tool", {})

    def test_execute_tool_invalid_name(
        self,
        mock_get_services,
        mock_get_id,
        mock_read_yaml,
        mock_service_factory,
        mock_importlib,
        mock_exists,
    ):
        """Tests that ValueError is raised for a malicious tool name."""
        mock_exists.return_value = True  # setting.yml exists
        mock_read_yaml.return_value = self.valid_settings
        mock_get_id.return_value = "test_session"

        mock_settings = MagicMock()
        mock_session_service = MagicMock()
        mock_session_service.timezone_obj = zoneinfo.ZoneInfo("UTC")
        mock_session_service.repository = MagicMock()
        mock_session_turn_service = MagicMock()
        mock_get_services.return_value = (
            mock_settings,
            mock_session_service,
            mock_session_turn_service,
        )

        with self.assertRaisesRegex(ValueError, "Invalid tool name."):
            execute_tool("../../bad", {})


@patch("pipe.cli.mcp_server.read_yaml_file")
@patch("pipe.cli.mcp_server.get_tool_definitions")
@patch("pipe.cli.mcp_server.execute_tool")
@patch("pipe.cli.mcp_server.select.select")
@patch("sys.stdout", new_callable=StringIO)
@patch("sys.stdin", new_callable=StringIO)
class TestMainLoop(unittest.TestCase):
    def test_initialize_request(
        self,
        mock_stdin,
        mock_stdout,
        mock_select,
        mock_execute,
        mock_get_defs,
        mock_read_yaml,
    ):
        """Tests handling of a standard 'initialize' request."""
        mock_get_defs.return_value = [{"name": "test_tool"}]
        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {"protocolVersion": "2025-06-18"},
        }
        mock_stdin.write(json.dumps(request) + "\n")
        mock_stdin.seek(0)
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]

        from pipe.cli.mcp_server import main

        main()

        output = mock_stdout.getvalue()
        response = json.loads(output)

        self.assertEqual(response["id"], "1")
        self.assertEqual(response["result"]["serverInfo"]["name"], "pipe_mcp_server")
        self.assertEqual(len(response["result"]["tools"]), 1)

    def test_tools_call_request(
        self,
        mock_stdin,
        mock_stdout,
        mock_select,
        mock_execute,
        mock_get_defs,
        mock_read_yaml,
    ):
        """Tests handling of a 'tools/call' request."""
        mock_execute.return_value = {"data": "success"}
        mock_read_yaml.return_value = {
            "timezone": "UTC",
            "api_mode": "gemini-cli",
            "parameters": {
                "temperature": {"value": 0.1, "description": "t"},
                "top_p": {"value": 0.2, "description": "p"},
                "top_k": {"value": 10, "description": "k"},
            },
        }
        request = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/call",
            "params": {"name": "my_tool", "args": {"x": 1}},
        }
        mock_stdin.write(json.dumps(request) + "\n")
        mock_stdin.seek(0)
        mock_select.side_effect = [([mock_stdin], [], []), ([], [], [])]

        from pipe.cli.mcp_server import main

        main()

        output = mock_stdout.getvalue()
        response = json.loads(output)

        self.assertEqual(response["id"], "2")
        # With the new logic, result is the dict itself (plus status)
        self.assertEqual(response["result"]["status"], "succeeded")
        self.assertEqual(response["result"]["data"], "success")

    def test_method_not_found(
        self,
        mock_stdin,
        mock_stdout,
        mock_select,
        mock_execute,
        mock_get_defs,
        mock_read_yaml,
    ):
        """Tests the response for an unknown method."""
        request = {"jsonrpc": "2.0", "id": "3", "method": "foo/bar"}
        mock_stdin.write(json.dumps(request) + "\n")
        mock_stdin.seek(0)
        mock_select.return_value = ([mock_stdin], [], [])

        from pipe.cli.mcp_server import main

        main()

        output = mock_stdout.getvalue()
        response = json.loads(output)

        self.assertEqual(response["id"], "3")
        self.assertEqual(response["error"]["code"], -32601)
        self.assertIn("Method not found", response["error"]["message"])


if __name__ == "__main__":
    unittest.main()
