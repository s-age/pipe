import os
import json

import google.genai as genai
from google.genai import types

from src.prompt_builder import PromptBuilder
from src.token_manager import TokenManager

def load_tools(project_root: str) -> list:
    tools_path = os.path.join(project_root, "tools.json")
    if not os.path.exists(tools_path):
        return []
    with open(tools_path, "r") as f:
        return json.load(f)

def call_gemini_api(settings: dict, session_data: dict, project_root: str, instruction: str, api_mode: str, multi_step_reasoning_enabled: bool) -> types.GenerateContentResponse:

    token_manager = TokenManager(settings=settings)

    builder = PromptBuilder(settings=settings, session_data=session_data, project_root=project_root, api_mode=api_mode, multi_step_reasoning_enabled=multi_step_reasoning_enabled)
    
    api_contents = builder.build()

    tools = load_tools(project_root)

    token_count = token_manager.count_tokens(api_contents, tools=tools)
    
    is_within_limit, message = token_manager.check_limit(token_count)
    print(f"Token Count: {message}")
    if not is_within_limit:
        raise ValueError("Prompt exceeds context window limit. Aborting.")

    # Build GenerationConfig from settings
    gen_config_params = {}
    if params := settings.get('parameters'):
        if temp := params.get('temperature'):
            gen_config_params['temperature'] = temp.get('value')
        if top_p := params.get('top_p'):
            gen_config_params['top_p'] = top_p.get('value')
        if top_k := params.get('top_k'):
            gen_config_params['top_k'] = top_k.get('value')
    
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
        response = client.models.generate_content(
            contents=api_contents,
            config=config,
            model=token_manager.model_name
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Error during Gemini API execution: {e}")
