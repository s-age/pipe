# This script utilizes the 'google-genai' library to interact with the Gemini API.
# It is important to note that 'google-genai' is the newer, recommended library,
# and should be used in place of the older 'google-generativeai' library to ensure
# access to the latest features and improvements.
# For reference, see: https://pypi.org/project/google-genai/

import importlib.util
import inspect
import logging
import os
import sys
from typing import Any, Union, get_args, get_type_hints

import google.genai as genai
from google.genai import types
from jinja2 import Environment, FileSystemLoader
from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService
from pipe.core.services.token_service import TokenService

# Configure logging
log_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "debug.log")
)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=log_file_path,
    filemode="w",  # Overwrite the log file on each run
)


def load_tools(project_root: str) -> list:
    """
    Scans the 'tools' directory to discover available tool scripts and generates
    JSON schema definitions compatible with google-genai for each tool.
    """
    tool_defs = []
    type_mapping = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
    }

    tools_dir = os.path.join(project_root, "src", "pipe", "core", "tools")

    try:
        filenames = os.listdir(tools_dir)
    except Exception:
        return []

    for filename in filenames:
        if not (filename.endswith(".py") and not filename.startswith("__")):
            continue

        tool_name = os.path.splitext(filename)[0]
        tool_file_path = os.path.join(tools_dir, filename)

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
                    if item_origin_type in (dict, dict):
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
                else:
                    mapped_type = type_mapping.get(param_type, "string")
                    properties[name] = {"type": mapped_type}

                if param.default is inspect.Parameter.empty and not is_optional:
                    required.append(name)

            tool_def = {
                "name": tool_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            tool_defs.append(tool_def)

        except Exception:
            pass

    return tool_defs


def call_gemini_api(session_service: SessionService, prompt_service: PromptService):
    settings = session_service.settings
    session_data = session_service.current_session
    project_root = session_service.project_root

    # Set the session ID as an environment variable to ensure it is passed to the
    # mcp_server.py when a tool is executed. This is crucial because the
    # google-genai library may spawn a new process for tool execution, and this
    # is the most reliable way to pass the current session context.
    os.environ["PIPE_SESSION_ID"] = session_data.session_id

    token_service = TokenService(settings=settings)

    # 1. Build the Prompt model using the service
    prompt_model = prompt_service.build_prompt(session_service)

    # 2. Render the Prompt model to a JSON string using the template
    template_env = Environment(
        loader=FileSystemLoader(
            os.path.join(prompt_service.project_root, "templates", "prompt")
        ),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = template_env.get_template("gemini_api_prompt.j2")

    context = prompt_model.model_dump()

    api_contents_string = template.render(session=context)

    tools = load_tools(project_root)
    logging.debug(f"Tools loaded by load_tools: {[tool['name'] for tool in tools]}")

    token_count = token_service.count_tokens(api_contents_string, tools=tools)

    is_within_limit, message = token_service.check_limit(token_count)
    print(f"Token Count: {message}", file=sys.stderr)
    if not is_within_limit:
        raise ValueError("Prompt exceeds context window limit. Aborting.")

    # Build GenerationConfig from settings, then override with session data
    gen_config_params = {
        "temperature": settings.parameters.temperature.value,
        "top_p": settings.parameters.top_p.value,
        "top_k": settings.parameters.top_k.value,
    }

    # 2. Override with session-specific hyperparameters
    if session_params := session_data.hyperparameters:
        if temp_obj := session_params.temperature:
            if temp_obj.value is not None:
                gen_config_params["temperature"] = temp_obj.value
        if top_p_obj := session_params.top_p:
            if top_p_obj.value is not None:
                gen_config_params["top_p"] = top_p_obj.value
        if top_k_obj := session_params.top_k:
            if top_k_obj.value is not None:
                gen_config_params["top_k"] = top_k_obj.value

    # tools.jsonからツールをロード
    loaded_tools_data = load_tools(project_root)

    # ロードしたツールデータをtypes.Toolオブジェクトに変換
    converted_tools = []
    for tool_data in loaded_tools_data:
        # parametersをtypes.Schemaオブジェクトに変換
        parameters_schema = types.Schema(**tool_data.get("parameters", {}))

        converted_tools.append(
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        parameters=parameters_schema,
                    )
                ]
            )
        )

    # GoogleSearchツールを追加 (GroundingとFunction Callingは両立しないため、
    # Function Callingツールのみを渡す)
    all_tools: list[Any] = converted_tools  # 既存ツールのみを渡す
    logging.debug(
        "Final tools passed to Gemini API: "
        f"{[func.name for tool in all_tools for func in tool.function_declarations]}"
    )

    config = types.GenerateContentConfig(
        tools=all_tools,  # <-- 統合したツールを渡す
        temperature=gen_config_params.get("temperature"),
        top_p=gen_config_params.get("top_p"),
        top_k=gen_config_params.get("top_k"),
    )

    client = genai.Client()

    try:
        stream = client.models.generate_content_stream(
            contents=api_contents_string, config=config, model=token_service.model_name
        )
        yield from stream
    except Exception as e:
        raise RuntimeError(f"Error during Gemini API execution: {e}")
