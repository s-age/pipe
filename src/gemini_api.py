import os
import json
from pathlib import Path
from google import genai
from google.genai import types

from src.prompt_builder import PromptBuilder
from src.token_manager import TokenManager

def call_gemini_api(settings: dict, session_data: dict, project_root: Path, instruction: str, multi_step_reasoning_enabled: bool) -> str:
    model_name = settings.get('model')
    if not model_name:
        raise ValueError("'model' not found in setting.yml")
    context_limit = settings.get('context_limit')
    if not context_limit:
        raise ValueError("'context_limit' not found in setting.yml")
    token_manager = TokenManager(model_name=model_name, limit=context_limit)

    builder = PromptBuilder(settings=settings, session_data=session_data, project_root=project_root, multi_step_reasoning_enabled=multi_step_reasoning_enabled)
    
    api_contents = builder.build_contents_for_api()

    token_count = token_manager.count_tokens(api_contents)
    
    is_within_limit, message = token_manager.check_limit(token_count)
    print(f"Token Count: {message}")
    if not is_within_limit:
        raise ValueError("Prompt exceeds context window limit. Aborting.")

    client = genai.Client()
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=api_contents
        )
        return response.text
    except Exception as e:
        raise RuntimeError(f"Error during Gemini API execution: {e}")
