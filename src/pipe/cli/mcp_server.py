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

import os
import sys
import json
import importlib.util
import traceback
import inspect
from typing import get_type_hints, Union, get_args, List, Dict
import warnings

# Add src directory to Python path BEFORE local imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from pipe.core.utils.file import read_yaml_file, append_to_text_file
from pipe.core.utils.datetime import get_current_timestamp
from pipe.core.services.session_service import SessionService
import select

# Suppress Pydantic's ArbitraryTypeWarning by matching the specific message
warnings.filterwarnings("ignore", message=".*is not a Python type.*\n")

# --- Global Paths ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
TOOLS_DIR = os.path.join(BASE_DIR, 'src', 'pipe', 'core', 'tools')
SESSIONS_DIR = os.path.join(BASE_DIR, 'sessions')

from pipe.core.models.settings import Settings

# --- Tool Definition Generation ---
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
    except Exception as e:
        return []

    for filename in filenames:
        if not (filename.endswith('.py') and not filename.startswith('__')):
            continue

        tool_name = os.path.splitext(filename)[0]
        tool_file_path = os.path.join(TOOLS_DIR, filename)

        try:
            spec = importlib.util.spec_from_file_location(f"pipe.core.tools.{tool_name}", tool_file_path)
            if spec is None:
                continue
            tool_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tool_module)
            
            if not hasattr(tool_module, tool_name):
                continue

            tool_function = getattr(tool_module, tool_name)
            sig = inspect.signature(tool_function)
            type_hints = get_type_hints(tool_function)

            description = inspect.getdoc(tool_function) or f"Executes the {tool_name} tool."

            properties = {}
            required = []

            for name, param in sig.parameters.items():
                if name in ['session_service', 'session_id', 'settings', 'project_root']:
                    continue

                param_type = type_hints.get(name, str)
                is_optional = False
                origin_type = getattr(param_type, '__origin__', None)

                if origin_type is Union:
                    union_args = get_args(param_type)
                    if len(union_args) == 2 and type(None) in union_args:
                        is_optional = True
                        param_type = next(t for t in union_args if t is not type(None))
                        origin_type = getattr(param_type, '__origin__', None)

                if origin_type in (list, List):
                    list_item_type = get_args(param_type)[0] if get_args(param_type) else str
                    item_origin_type = getattr(list_item_type, '__origin__', None)
                    if item_origin_type in (dict, Dict):
                        properties[name] = {"type": "array", "items": {"type": "object"}}
                    else:
                        mapped_item_type = type_mapping.get(list_item_type, "string")
                        properties[name] = {"type": "array", "items": {"type": mapped_item_type}}
                elif origin_type in (dict, Dict):
                     properties[name] = {"type": "object", "properties": {}}
                else:
                    mapped_type = type_mapping.get(param_type, "string")
                    properties[name] = {"type": mapped_type}

                if param.default is inspect.Parameter.empty and not is_optional:
                    required.append(name)

            tool_def = {
                "name": tool_name,
                "description": description,
                "inputSchema": {"type": "object", "properties": properties, "required": required}
            }
            tool_defs.append(tool_def)

        except Exception as e:
            # Continue to next tool
            pass
    
    return tool_defs

# --- Tool Execution ---
def get_latest_session_id():
    """
    Scans the sessions directory and returns the most recently modified session ID.
    PRIORITY: Checks for a session ID in the environment variable 'FIXED_SESSION_ID' or 'GEMINI_SESSION_ID' first.
    """
    # 1. 環境変数からセッションIDを取得する（Gemini-CLIから渡される可能性のある変数名）
    session_id_from_env = os.getenv('FIXED_SESSION_ID') or os.getenv('GEMINI_SESSION_ID')
    if session_id_from_env:
        return session_id_from_env

    # 2. 環境変数にない場合、従来のロジックで最新のセッションIDを取得
    try:
        files = [os.path.join(SESSIONS_DIR, f) for f in os.listdir(SESSIONS_DIR) if f.endswith('.json')]
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        return os.path.splitext(os.path.basename(latest_file))[0]
    except FileNotFoundError:
        return None

def execute_tool(tool_name, arguments):
    """
    Dynamically imports and executes a specified tool function with the given arguments.

    This function handles the core logic of a 'tools/call' request. It performs the following steps:
    1.  Retrieves the current session context.
    2.  Logs the tool call initiation to the session's history pool.
    3.  Validates the tool name and locates the corresponding Python file in the 'tools' directory.
    4.  Dynamically imports the file as a module.
    5.  Retrieves the tool function from the module.
    6.  Prepares the final arguments for the function call by injecting necessary server-side
        dependencies (e.g., `session_service`, `settings`) into the arguments received
        from the client.
    7.  Executes the tool function with the prepared arguments.
    8.  Logs the result (success or failure) of the tool execution to the history pool.
    9.  Returns the result to the main loop to be sent back to the client.
    """
    project_root = BASE_DIR
    config_path = os.path.join(project_root, 'setting.yml')
    settings_dict = read_yaml_file(config_path)
    settings = Settings(**settings_dict)

    session_id = get_latest_session_id()
    session_service = SessionService(project_root, settings)

    # Log the start of the tool call to the pool
    if session_id:
        try:
            response_string = f"{tool_name}({json.dumps(arguments, ensure_ascii=False)})"
            function_calling_turn = {
                "type": "function_calling",
                "response": response_string,
                "timestamp": get_current_timestamp(session_service.timezone_obj)
            }
            session_service.add_to_pool(session_id, function_calling_turn)
        except Exception:
            # Avoid crashing the server if logging fails
            pass

    if not session_id:
        # Allow tools that don't require a session to run
        pass

    if '..' in tool_name or '/' in tool_name:
        raise ValueError("Invalid tool name.")

    tool_file_path = os.path.join(TOOLS_DIR, f"{tool_name}.py")
    if not os.path.exists(tool_file_path):
        raise FileNotFoundError(f"Tool '{tool_name}' not found.")

    spec = importlib.util.spec_from_file_location(tool_name, tool_file_path)
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
            project_root
        )
        


        result = tool_function(**final_args)

        # Log the end of the tool call to the pool
        if session_id:
            try:
                # Format the response similarly to takt
                if isinstance(result, dict) and 'error' in result and result['error'] != '(none)':
                    formatted_response = {"status": "failed", "message": result['error']}
                else:
                    message_content = result.get('message') if isinstance(result, dict) and 'message' in result else result
                    formatted_response = {"status": "succeeded", "message": message_content}

                tool_response_turn = {
                    "type": "tool_response",
                    "name": tool_name,
                    "response": formatted_response,
                    "timestamp": get_current_timestamp(session_service.timezone_obj)
                }
                session_service.add_to_pool(session_id, tool_response_turn)
            except Exception:
                # Avoid crashing the server if logging fails
                pass
        
        return result
    else:
        raise NotImplementedError(f"Function '{tool_name}' not found in tool '{tool_name}'.")

def prepare_tool_arguments(tool_function, client_arguments, session_service, session_id, settings, project_root):
    """
    ツール関数のシグネチャを検査し、必要に応じてサーバー引数を注入して、
    最終的な引数ディクショナリを構築する。
    """
    
    sig = inspect.signature(tool_function)
    params = sig.parameters
    
    # クライアントからの引数（arguments）をベースとする
    final_arguments = client_arguments.copy()
    
    # ツール関数が定義しているパラメーターに基づいてサーバー引数を注入
    if 'session_service' in params:
        final_arguments['session_service'] = session_service

    # session_id はクライアントから指定されていない場合のみ注入する
    if 'session_id' in params and 'session_id' not in final_arguments:
        final_arguments['session_id'] = session_id

    if 'settings' in params:
        final_arguments['settings'] = settings
    if 'project_root' in params:
        final_arguments['project_root'] = project_root
        
    return final_arguments

# --- Main Stdio Loop ---
def main():
    """
    The main entry point and I/O loop for the MCP server.

    This function continuously reads lines from standard input, expecting each line
    to be a valid JSON-RPC 2.0 request object. It parses the request, determines
    the requested method, and dispatches it to the appropriate handler.

    Supported MCP methods:
    - `initialize`: Responds with server capabilities and a list of all available tools.
    - `tools/list`: Responds with a fresh list of available tools.
    - `tools/call`: Executes a specific tool with provided arguments using the `execute_tool` function.
    - `ping`: A simple health check method.
    - `notifications/initialized`: A notification from the client that it has initialized.

    For each request that requires a response, this function formats the response as a
    JSON-RPC 2.0 object and writes it to standard output, followed by a newline and a flush,
    ensuring the client receives it promptly.

    The loop includes error handling to catch JSON decoding errors or exceptions during
    tool execution, formatting them into standard JSON-RPC error responses. It also
    logs unexpected server errors to a file to avoid polluting the stdio channel.
    """
    sys.path.insert(0, BASE_DIR)
    while True:
        try:
            # Wait for input on stdin for 10 seconds
            ready, _, _ = select.select([sys.stdin], [], [], None)
            if not ready:
                break # Exit if timeout is reached

            line = sys.stdin.readline()
            if not line:
                break # Exit if stdin is closed

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
                        "capabilities": {
                            "tools": {
                                "call": True,
                                "list": True
                            }
                        },
                        "serverInfo": {"name": "pipe_mcp_server", "version": "0.1.0"},
                        "tools": get_tool_definitions(),
                        "prompts": [],
                    }
                }
            elif method == "tools/list":
                tool_defs = get_tool_definitions()
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": tool_defs, "prompts": []}
                }
            elif method == "notifications/initialized":
                pass # Simply continue the loop
            elif method == "ping":
                response = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get('name')
                arguments = params.get('args', {})
                if not arguments:
                    arguments = params.get('arguments', {}) # 'args'が空なら'arguments'を試す
                
                try:
                    tool_result = execute_tool(tool_name, arguments)
                    
                    if isinstance(tool_result, dict) and 'error' in tool_result:
                        error_message = tool_result.get('error', 'Tool execution failed.')
                        response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": f"Tool '{tool_name}' failed: {error_message}"}}
                    else:
                        # Load settings to check api_mode and format response accordingly
                        project_root = BASE_DIR
                        config_path = os.path.join(project_root, 'setting.yml')
                        settings_dict = read_yaml_file(config_path)
                        settings = Settings(**settings_dict)
                        api_mode = settings.api_mode

                        if api_mode == 'gemini-cli':
                            # Transform the result to the format expected by the gemini-cli client
                            transformed_result = {
                                "isError": False,
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(tool_result)
                                    }
                                ]
                            }
                            response = {"jsonrpc": "2.0", "id": req_id, "result": transformed_result}
                        else:
                            # Keep the original structure for other modes
                            response = {"jsonrpc": "2.0", "id": req_id, "result": {"status": "succeeded", "result": tool_result}}
                except Exception as e:
                    response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}
            elif method == "run_tool":
                params = request.get("params", {})
                tool_name = params.get('tool_name')
                arguments = params.get('arguments', {})

                try:
                    tool_result = execute_tool(tool_name, arguments)

                    if isinstance(tool_result, dict) and 'error' in tool_result:
                        error_message = tool_result.get('error', 'Tool execution failed.')
                        response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": f"Tool '{tool_name}' failed: {error_message}"}}
                    else:
                        response = {"jsonrpc": "2.0", "id": req_id, "result": {"status": "succeeded", "result": tool_result}}
                except Exception as e:
                    response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}
            else:
                response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

            if response:
                payload = json.dumps(response)
                
                # sys.stdout.writeを使用し、write後に明示的にflushする
                sys.stdout.write(payload + '\n') # 標準的なJSON-RPC over stdioでは末尾に改行を付けることが多い
                sys.stdout.flush()

        except json.JSONDecodeError:
            # Ignore lines that are not valid JSON
            pass
        except Exception:
            # Log other exceptions to a file to not interfere with stdio
            append_to_text_file("mcp_server_error.log", traceback.format_exc() + "\n")

if __name__ == "__main__":
    main()