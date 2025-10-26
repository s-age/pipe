# This script utilizes the 'google-genai' library to interact with the Gemini API.
# It is important to note that 'google-genai' is the newer, recommended library,
# and should be used in place of the older 'google-generativeai' library to ensure
# access to the latest features and improvements.
# For reference, see: https://pypi.org/project/google-genai/

import os
import json
import sys

import google.genai as genai
from google.genai import types

import importlib.util
import inspect
from typing import get_type_hints, Union, get_args, List, Dict

from pipe.core.models.session import Session
from pipe.core.models.settings import Settings
from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService
from pipe.core.token_manager import TokenManager
from pipe.core.utils.file import read_json_file
from jinja2 import Environment, FileSystemLoader

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
    
    tools_dir = os.path.join(project_root, 'src', 'pipe', 'core', 'tools')

    try:
        filenames = os.listdir(tools_dir)
    except Exception as e:
        return []

    for filename in filenames:
        if not (filename.endswith('.py') and not filename.startswith('__')):
            continue

        tool_name = os.path.splitext(filename)[0]
        tool_file_path = os.path.join(tools_dir, filename)

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
                "parameters": {
                    "type": "OBJECT",
                    "properties": properties,
                    "required": required
                }
            }
            tool_defs.append(tool_def)

        except Exception as e:
            pass
    
    return tool_defs

def call_gemini_api(session_service: SessionService, prompt_service: PromptService):
    settings = session_service.settings
    session_data = session_service.current_session
    project_root = session_service.project_root
    multi_step_reasoning_enabled = session_data.multi_step_reasoning_enabled
    
    token_manager = TokenManager(settings=settings)

    # 1. Build the Prompt model using the service
    prompt_model = prompt_service.build_prompt(session_service)

    # 2. Render the Prompt model to a JSON string using the template
    template_env = Environment(
        loader=FileSystemLoader(os.path.join(prompt_service.project_root, 'templates', 'prompt')),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = template_env.get_template('gemini_api_prompt.j2')
    
    context = prompt_model.model_dump()
    
    api_contents_string = template.render(session=context)

    tools = load_tools(project_root)

    token_count = token_manager.count_tokens(api_contents_string, tools=tools)
    
    is_within_limit, message = token_manager.check_limit(token_count)
    print(f"Token Count: {message}", file=sys.stderr)
    if not is_within_limit:
        raise ValueError("Prompt exceeds context window limit. Aborting.")

    # Build GenerationConfig from settings, then override with session data
    gen_config_params = {
        'temperature': settings.parameters.temperature.value,
        'top_p': settings.parameters.top_p.value,
        'top_k': settings.parameters.top_k.value
    }

    # 2. Override with session-specific hyperparameters
    if session_params := session_data.hyperparameters:
        if temp := session_params.temperature:
            gen_config_params['temperature'] = temp.value
        if top_p := session_params.top_p:
            gen_config_params['top_p'] = top_p.value
        if top_k := session_params.top_k:
            gen_config_params['top_k'] = top_k.value
    
    # tools.jsonからツールをロード
    loaded_tools_data = load_tools(project_root)

    # ロードしたツールデータをtypes.Toolオブジェクトに変換
    converted_tools = []
    for tool_data in loaded_tools_data:
        # parametersをtypes.Schemaオブジェクトに変換
        parameters_schema = types.Schema(**tool_data.get('parameters', {}))
        
        converted_tools.append(types.Tool(function_declarations=[types.FunctionDeclaration(
            name=tool_data['name'],
            description=tool_data.get('description', ''),
            parameters=parameters_schema
        )]))

    # GoogleSearchツールを追加 (GroundingとFunction Callingは両立しないため、Function Callingツールのみを渡す)
    all_tools = converted_tools # 既存ツールのみを渡す

    config = types.GenerateContentConfig(
        tools=all_tools, # <-- 統合したツールを渡す
        temperature=gen_config_params.get('temperature'),
        top_p=gen_config_params.get('top_p'),
        top_k=gen_config_params.get('top_k')
    )

    client = genai.Client()

    try:
        stream = client.models.generate_content_stream(
            contents=api_contents_string,
            config=config,
            model=token_manager.model_name
        )
        yield from stream
    except Exception as e:
        raise RuntimeError(f"Error during Gemini API execution: {e}")
