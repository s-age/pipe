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
    
    # 1. Build the system context part
    full_prompt_obj = builder.build()
    system_context_obj = {k: v for k, v in full_prompt_obj.items() if k not in ['conversation_history', 'current_task']}
    system_prompt_str = "## SYSTEM CONTEXT & RULES (JSON) ##\n"
    system_prompt_str += json.dumps(system_context_obj, indent=2, ensure_ascii=False)

    # 2. Build the conversation turns part
    conversation_contents = builder.build_conversation_turns_for_api()

    # 3. Combine them for the final API contents
    api_contents = [
        {'role': 'user', 'parts': [{'text': system_prompt_str}]},
        {'role': 'model', 'parts': [{'text': "Understood. I will follow all instructions and context provided."}]}
    ] + conversation_contents

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
    
    generation_config = genai.GenerationConfig(**gen_config_params)

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