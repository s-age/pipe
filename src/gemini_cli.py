import json
import subprocess
import sys
from pathlib import Path

from src.prompt_builder import PromptBuilder

def call_gemini_cli(settings: dict, session_data: dict, project_root: Path, instruction: str, api_mode: str, multi_step_reasoning_enabled: bool) -> str:
    model_name = settings.get('model')
    if not model_name:
        raise ValueError("'model' not found in setting.yml")

    builder = PromptBuilder(settings=settings, session_data=session_data, project_root=project_root, api_mode=api_mode, multi_step_reasoning_enabled=multi_step_reasoning_enabled)
    
    final_prompt = builder.build()

    command = ['gemini', '-m', model_name, '-p', final_prompt]
    if settings.get('yolo', False):
        command.insert(1, '-y')
    try:
        process = subprocess.run(
            command, capture_output=True, text=True, check=True, encoding='utf-8'
        )
        model_response_text = process.stdout
        if process.stderr:
            print(f"Warning from gemini-cli: {process.stderr}", file=sys.stderr)
        return model_response_text
    except FileNotFoundError:
        raise RuntimeError("Error: 'gemini' command not found. Make sure it's in your PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error during gemini-cli execution: {e.stderr}")
