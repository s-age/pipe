import os
import json
from pathlib import Path
import google.generativeai as genai
from google.genai import types

from src.prompt_builder import PromptBuilder
from src.token_manager import TokenManager

def load_tools(project_root: Path) -> list:
    tools_path = project_root / "tools.json"
    if not tools_path.exists():
        return []
    with open(tools_path, "r") as f:
        return json.load(f)

def call_gemini_api(settings: dict, session_data: dict, project_root: Path, instruction: str, api_mode: str, multi_step_reasoning_enabled: bool) -> types.GenerateContentResponse:
    model_name = settings.get('model')
    if not model_name:
        raise ValueError("'model' not found in setting.yml")
    context_limit = settings.get('context_limit')
    if not context_limit:
        raise ValueError("'context_limit' not found in setting.yml")
    token_manager = TokenManager(model_name=model_name, limit=context_limit)

    builder = PromptBuilder(settings=settings, session_data=session_data, project_root=project_root, api_mode=api_mode, multi_step_reasoning_enabled=multi_step_reasoning_enabled)
    
    api_contents = builder.build_contents_for_api()

    token_count = token_manager.count_tokens(api_contents)
    
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
    
    generation_config = genai.GenerationConfig(**gen_config_params)

    tools = load_tools(project_root)

    model = genai.GenerativeModel(
        model_name=model_name, 
        tools=tools,
        generation_config=generation_config
    )

    try:
        response = model.generate_content(
            contents=api_contents,
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Error during Gemini API execution: {e}")
