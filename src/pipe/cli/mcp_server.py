# This script implements a server that adheres to the Model Context Protocol (MCP).
# MCP is an open-standard, JSON-RPC 2.0 based protocol designed to standardize
# the communication between a client (e.g., a large language model) and a server
# that provides access to a set of tools.
#
# The server operates over standard input/output and has several key responsibilities:
# 1.  **Tool Discovery:** It dynamically discovers and exposes all available tools
#     from the `src/pipe/core/tools` directory.
# 2.  **MCP Communication:** It listens for JSON-RPC requests from an MCP client,
#     advertises the tools via the 'initialize' and 'tools/list' methods, and
#     executes them upon receiving a 'tools/call' request.
# 3.  **Automatic Logging:** It automatically logs all tool calls (`function_calling`)
#     and their results (`tool_response`) to the active session's history pool,
#     ensuring complete transparency of agent actions.
#
# This architecture allows an AI model to leverage external tools in a standardized way.
#
# For more on the tool architecture, see `src/pipe/core/tools/README.md`.
# For more on the MCP protocol itself, refer to its official specification.

import importlib.util
import inspect
import json
import os
import sys
import traceback
import warnings
from functools import lru_cache
from typing import TYPE_CHECKING, Union, get_args, get_type_hints

if TYPE_CHECKING:
    from pipe.core.factories.service_factory import ServiceFactory
    from pipe.core.models.settings import Settings

# Suppress Pydantic warnings early, before importing any pydantic models
warnings.filterwarnings("ignore", message=".*is not a Python type.*\n")
warnings.filterwarnings("ignore", message='Field name .* shadows an attribute')

from pydantic import BaseModel  # noqa: E402

# Add src directory to Python path BEFORE local imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import select  # noqa: E402

if not TYPE_CHECKING:
    from pipe.core.factories.service_factory import ServiceFactory  # noqa: E402
    from pipe.core.models.settings import Settings  # noqa: E402

from pipe.core.utils.datetime import get_current_timestamp  # noqa: E402
from pipe.core.utils.file import append_to_text_file, read_yaml_file  # noqa: E402

# --- Global Paths ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TOOLS_DIR = os.path.join(BASE_DIR, "src", "pipe", "core", "tools")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

# --- Global Services (initialized once) ---
_SETTINGS: "Settings | None" = None
_SERVICE_FACTORY: "ServiceFactory | None" = None
_SESSION_SERVICE: object | None = None


def initialize_services():
    """
    Initialize global services once to avoid repeated file I/O and object creation.
    This significantly improves performance for tool execution.
    """
    global _SETTINGS, _SERVICE_FACTORY, _SESSION_SERVICE
    if _SETTINGS is None:
        project_root = BASE_DIR
        config_path = os.path.join(project_root, "setting.yml")
        settings_dict = read_yaml_file(config_path)
        _SETTINGS = Settings(**settings_dict)
        _SERVICE_FACTORY = ServiceFactory(project_root, _SETTINGS)
        _SESSION_SERVICE = _SERVICE_FACTORY.create_session_service()


def get_services():
    """Get initialized services, initializing them if needed."""
    if _SETTINGS is None:
        initialize_services()
    return _SETTINGS, _SESSION_SERVICE


# --- Tool Definition Generation ---
@lru_cache(maxsize=1)
def get_tool_definitions():
    """
    Scans the 'tools' directory to discover available tool scripts and generates
    OpenAPI-compatible JSON schema definitions for each tool.

    This function iterates through Python files in the TOOLS_DIR, dynamically
    imports them as modules, and inspects the signature of the function matching
    the file name. It uses type hints and docstrings to construct a schema
    that describes the tool's name, purpose, input parameters, and required arguments.

    This list of definitions is then sent to the MCP client during the 'initialize'
    and 'tools/list' calls, allowing the client (and the AI model) to understand
    what tools are available and how to use them.

    Results are cached to avoid repeated filesystem scans and module imports.
    """
    tool_defs = []
    type_mapping = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
    }

    try:
        filenames = os.listdir(TOOLS_DIR)
    except Exception:
        return []

    for filename in filenames:
        if not (filename.endswith(".py") and not filename.startswith("__")):
            continue

        tool_name = os.path.splitext(filename)[0]
        tool_file_path = os.path.join(TOOLS_DIR, filename)

        try:
            spec = importlib.util.spec_from_file_location(
                f"pipe.core.tools.{tool_name}", tool_file_path
            )
            if not spec or not spec.loader:
                continue
            tool_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tool_module)

            if not hasattr(tool_module, tool_name):
                continue

            tool_function = getattr(tool_module, tool_name)
            sig = inspect.signature(tool_function)
            type_hints = get_type_hints(tool_function)

            description = (
                inspect.getdoc(tool_function) or f"Executes the {tool_name} tool."
            )

            properties = {}
            required = []

            for name, param in sig.parameters.items():
                if name in [
                    "session_service",
                    "session_id",
                    "settings",
                    "project_root",
                ]:
                    continue

                param_type = type_hints.get(name, str)
                is_optional = False
                origin_type = getattr(param_type, "__origin__", None)

                if origin_type is Union:
                    union_args = get_args(param_type)
                    if len(union_args) == 2 and type(None) in union_args:
                        is_optional = True
                        param_type = next(t for t in union_args if t is not type(None))
                        origin_type = getattr(param_type, "__origin__", None)

                if origin_type in (list, list):
                    list_item_type = (
                        get_args(param_type)[0] if get_args(param_type) else str
                    )
                    item_origin_type = getattr(list_item_type, "__origin__", None)
                    if inspect.isclass(list_item_type) and issubclass(
                        list_item_type, BaseModel
                    ):
                        properties[name] = {
                            "type": "array",
                            "items": list_item_type.model_json_schema(),
                        }
                    elif item_origin_type in (dict, dict):
                        properties[name] = {
                            "type": "array",
                            "items": {"type": "object"},
                        }
                    else:
                        mapped_item_type = type_mapping.get(list_item_type, "string")
                        properties[name] = {
                            "type": "array",
                            "items": {"type": mapped_item_type},
                        }
                elif origin_type in (dict, dict):
                    properties[name] = {"type": "object", "properties": {}}
                elif inspect.isclass(param_type) and issubclass(param_type, BaseModel):
                    properties[name] = param_type.model_json_schema()
                else:
                    mapped_type = type_mapping.get(param_type, "string")
                    properties[name] = {"type": mapped_type}

                if param.default is inspect.Parameter.empty and not is_optional:
                    required.append(name)

            tool_def = {
                "name": tool_name,
                "description": description,
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            tool_defs.append(tool_def)

        except Exception:
            # Continue to next tool
            pass

    return tool_defs


# --- Tool Execution ---
def get_latest_session_id():
    """
    Scans the sessions directory and returns the most recently modified session ID.
    PRIORITY: Checks for a session ID in the environment variable
    'PIPE_SESSION_ID' first.
    """
    # 1. Get session ID from environment variable (passed from Gemini-CLI)
    session_id_from_env = os.getenv("PIPE_SESSION_ID")
    if session_id_from_env:
        return session_id_from_env

    # 2. If not in environment variable, get latest session ID using traditional logic
    try:
        files = [
            os.path.join(SESSIONS_DIR, f)
            for f in os.listdir(SESSIONS_DIR)
            if f.endswith(".json")
        ]
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        return os.path.splitext(os.path.basename(latest_file))[0]
    except FileNotFoundError:
        return None


def execute_tool(tool_name, arguments):
    """
    Dynamically imports and executes a specified tool function with the given
    arguments.

    This function handles the core logic of a 'tools/call' request. It performs
    the following steps:
    1.  Retrieves the current session context.
    2.  Logs the tool call initiation to the session's history pool.
    3.  Validates the tool name and locates the corresponding Python file in the
        'tools' directory.
    4.  Dynamically imports the file as a module.
    5.  Retrieves the tool function from the module.
    6.  Prepares the final arguments for the function call by injecting necessary
        server-side dependencies (e.g., `session_service`, `settings`) into the
        arguments received from the client.
    7.  Executes the tool function with the prepared arguments.
    8.  Logs the result (success or failure) of the tool execution to the
        history pool.
    9.  Returns the result to the main loop to be sent back to the client.
    """
    # Use globally initialized services for performance
    settings, session_service = get_services()
    project_root = BASE_DIR
    session_id = get_latest_session_id()

    # Log the start of the tool call to the pool
    if session_id:
        try:
            from pipe.core.models.turn import FunctionCallingTurn

            response_string = (
                f"{tool_name}({json.dumps(arguments, ensure_ascii=False)})"
            )
            function_calling_turn = FunctionCallingTurn(
                type="function_calling",
                response=response_string,
                timestamp=get_current_timestamp(session_service.timezone_obj),
            )
            # Add the function_calling turn to the temporary pool.
            # Storing tool-related turns (function_calling, tool_response) in the
            # pool is crucial. If we were to write them directly to the main
            # 'turns' list, they would be recorded *before* the final
            # model_response, creating an incorrect sequence like:
            # user_task -> function_calling -> tool_response -> user_task ->
            # model_response.
            # The pool acts as a staging area, allowing the dispatcher to merge
            # these turns back in the correct final order:
            # user_task -> function_calling -> tool_response -> model_response.
            session_service.add_to_pool(session_id, function_calling_turn)
        except Exception:
            # Avoid crashing the server if logging fails
            pass

    if not session_id:
        # Allow tools that don't require a session to run
        pass

    if ".." in tool_name or "/" in tool_name:
        raise ValueError("Invalid tool name.")

    tool_file_path = os.path.join(TOOLS_DIR, f"{tool_name}.py")
    if not os.path.exists(tool_file_path):
        raise FileNotFoundError(f"Tool '{tool_name}' not found.")

    spec = importlib.util.spec_from_file_location(tool_name, tool_file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not create module spec for tool '{tool_name}'")
    tool_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool_module)

    if hasattr(tool_module, tool_name):
        tool_function = getattr(tool_module, tool_name)

        final_args = prepare_tool_arguments(
            tool_function,
            arguments,
            session_service,
            session_id,
            settings,
            project_root,
        )

        result = tool_function(**final_args)

        # Log the end of the tool call to the pool
        if session_id:
            try:
                # Format the response similarly to takt
                if (
                    isinstance(result, dict)
                    and "error" in result
                    and result["error"] != "(none)"
                ):
                    formatted_response = {
                        "status": "failed",
                        "message": result["error"],
                    }
                else:
                    message_content = (
                        result.get("message")
                        if isinstance(result, dict) and "message" in result
                        else result
                    )
                    formatted_response = {
                        "status": "succeeded",
                        "message": message_content,
                    }

                from pipe.core.models.turn import ToolResponseTurn

                tool_response_turn = ToolResponseTurn(
                    type="tool_response",
                    name=tool_name,
                    response=formatted_response,
                    timestamp=get_current_timestamp(session_service.timezone_obj),
                )
                # Add the tool_response turn to the temporary pool.
                # This follows the same logic as the function_calling turn, ensuring
                # the complete tool interaction sequence is staged correctly before
                # being merged by the dispatcher.
                session_service.add_to_pool(session_id, tool_response_turn)
            except Exception:
                # Avoid crashing the server if logging fails
                pass

        return result
    else:
        raise NotImplementedError(
            f"Function '{tool_name}' not found in tool '{tool_name}'."
        )


def prepare_tool_arguments(
    tool_function, client_arguments, session_service, session_id, settings, project_root
):
    """
    Inspects the tool function signature and injects server arguments as needed
    to build the final arguments dictionary.
    """

    sig = inspect.signature(tool_function)
    params = sig.parameters

    # Base arguments from client
    final_arguments = client_arguments.copy()

    # Inject server arguments based on tool function's defined parameters
    if session_service and "session_service" in params:
        final_arguments["session_service"] = session_service

    # Only inject session_id if not specified by client
    if "session_id" in params and "session_id" not in final_arguments:
        final_arguments["session_id"] = session_id

    if "settings" in params:
        final_arguments["settings"] = settings
    if "project_root" in params:
        final_arguments["project_root"] = project_root

    return final_arguments


def format_mcp_tool_result(result, is_error=False):
    """
    Format tool result in MCP-compliant format.
    Always returns content array as per MCP specification.
    """
    if isinstance(result, str):
        content_text = result
    else:
        content_text = json.dumps(result, ensure_ascii=False)

    return {
        "content": [{"type": "text", "text": content_text}],
        "isError": is_error
    }


# --- Main Stdio Loop ---
def main():
    """
    The main entry point and I/O loop for the MCP server.

    This function continuously reads lines from standard input, expecting each
    line to be a valid JSON-RPC 2.0 request object. It parses the request,
    determines the requested method, and dispatches it to the appropriate
    handler.

    Supported MCP methods:
    - `initialize`: Responds with server capabilities and a list of all
      available tools.
    - `tools/list`: Responds with a fresh list of available tools.
    - `tools/call`: Executes a specific tool with provided arguments using the
      `execute_tool` function.
    - `ping`: A simple health check method.
    - `notifications/initialized`: A notification from the client that it has
      initialized.

    For each request that requires a response, this function formats the
    response as a JSON-RPC 2.0 object and writes it to standard output,
    followed by a newline and a flush, ensuring the client receives it
    promptly.

    The loop includes error handling to catch JSON decoding errors or
    exceptions during tool execution, formatting them into standard JSON-RPC
    error responses. It also logs unexpected server errors to a file to avoid
    polluting the stdio channel.
    """
    sys.path.insert(0, BASE_DIR)
    while True:
        try:
            # Wait for input on stdin for 10 seconds
            ready, _, _ = select.select([sys.stdin], [], [], None)
            if not ready:
                break  # Exit if timeout is reached

            line = sys.stdin.readline()
            if not line:
                break  # Exit if stdin is closed

            request = json.loads(line)
            response = None

            method = request.get("method")
            req_id = request.get("id")

            if method == "initialize":
                params = request.get("params", {})
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": params.get("protocolVersion", "2025-06-18"),
                        "capabilities": {"tools": {"call": True, "list": True}},
                        "serverInfo": {"name": "pipe_mcp_server", "version": "0.1.0"},
                        "tools": get_tool_definitions(),
                        "prompts": [],
                    },
                }
            elif method == "tools/list":
                tool_defs = get_tool_definitions()
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": tool_defs, "prompts": []},
                }
            elif method == "notifications/initialized":
                pass  # Simply continue the loop
            elif method == "ping":
                response = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("args", {})
                if not arguments:
                    arguments = params.get(
                        "arguments", {}
                    )  # Try 'arguments' if 'args' is empty

                try:
                    tool_result = execute_tool(tool_name, arguments)

                    # Check if tool result indicates an error
                    if isinstance(tool_result, dict) and "error" in tool_result:
                        error_message = tool_result.get(
                            "error", "Tool execution failed."
                        )
                        # Return MCP-compliant error response
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": format_mcp_tool_result(
                                {"error": error_message}, is_error=True
                            ),
                        }
                    else:
                        # Return MCP-compliant success response
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": format_mcp_tool_result(
                                tool_result, is_error=False
                            ),
                        }
                except Exception as e:
                    # Return MCP-compliant error response for exceptions
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": format_mcp_tool_result(
                            {"error": str(e)}, is_error=True
                        ),
                    }
            elif method == "run_tool":
                params = request.get("params", {})
                tool_name = params.get("tool_name")
                arguments = params.get("arguments", {})

                try:
                    tool_result = execute_tool(tool_name, arguments)

                    if isinstance(tool_result, dict) and "error" in tool_result:
                        error_message = tool_result.get(
                            "error", "Tool execution failed."
                        )
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "error": {
                                "code": -32000,
                                "message": (
                                    f"Tool '{tool_name}' failed: {error_message}"
                                ),
                            },
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {"status": "succeeded", "result": tool_result},
                        }
                except Exception as e:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32603, "message": str(e)},
                    }
            else:
                # Only send error response if request has an id (not a notification)
                if req_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}",
                        },
                    }

            # JSON-RPC 2.0: Only send response if request had an id
            # (notifications don't get responses)
            if response and req_id is not None:
                payload = json.dumps(response)

                # Use sys.stdout.write and explicitly flush after writing
                sys.stdout.write(
                    payload + "\n"
                )  # Standard JSON-RPC over stdio typically adds a newline at the end
                sys.stdout.flush()

        except json.JSONDecodeError:
            # Ignore lines that are not valid JSON
            pass
        except Exception:
            # Log other exceptions to a file to not interfere with stdio
            append_to_text_file("mcp_server_error.log", traceback.format_exc() + "\n")


if __name__ == "__main__":
    main()
