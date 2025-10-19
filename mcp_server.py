import os
import sys
import json
import importlib.util
import traceback
import inspect
import os
import sys
import json
import importlib.util
import traceback
import inspect
from typing import get_type_hints, Union, get_args, List, Dict
from src.utils import read_yaml_file
import warnings

# Suppress Pydantic's ArbitraryTypeWarning by matching the specific message
warnings.filterwarnings("ignore", message=".*is not a Python type.*")

# Add src directory to Python path to import session_manager
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from session_manager import SessionManager

# --- Global Paths ---
BASE_DIR = os.path.dirname(__file__)
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')
SESSIONS_DIR = os.path.join(BASE_DIR, 'sessions')

# --- Tool Definition Generation ---
def get_tool_definitions():
    """Scans the tools directory and builds a list of OpenAPI-compatible tool definitions."""
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
            spec = importlib.util.spec_from_file_location(tool_name, tool_file_path)
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
                if name in ['session_manager', 'session_id', 'settings', 'project_root']:
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
    """Dynamically imports and executes a tool function."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(project_root, 'setting.yml')
    settings = read_yaml_file(config_path)

    session_id = get_latest_session_id()
    if not session_id:
        # Allow tools that don't require a session to run
        pass

    session_manager = SessionManager(SESSIONS_DIR)

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
            session_manager, 
            session_id, 
            settings, 
            project_root
        )
        


        result = tool_function(**final_args)
        return result
    else:
        raise NotImplementedError(f"Function '{tool_name}' not found in tool '{tool_name}'.")

def prepare_tool_arguments(tool_function, client_arguments, session_manager, session_id, settings, project_root):
    """
    ツール関数のシグネチャを検査し、必要に応じてサーバー引数を注入して、
    最終的な引数ディクショナリを構築する。
    """
    
    sig = inspect.signature(tool_function)
    params = sig.parameters
    
    # クライアントからの引数（arguments）をベースとする
    final_arguments = client_arguments.copy()
    
    # ツール関数が定義しているパラメーターに基づいてサーバー引数を注入
    if 'session_manager' in params:
        final_arguments['session_manager'] = session_manager

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
    """Main loop to read from stdin, process JSON-RPC, and write to stdout."""
    import select

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
            with open("mcp_server_error.log", "a") as f:
                f.write(traceback.format_exc() + "\n")

if __name__ == "__main__":
    main()
