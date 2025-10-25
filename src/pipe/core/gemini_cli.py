# This script acts as a wrapper for the official Google Gemini CLI tool.
# Its main purpose is to construct a detailed prompt using the PromptBuilder
# and then execute the 'gemini' command-line tool as a subprocess with
# the generated prompt.
#
# This allows the application to leverage the functionality of the official CLI
# while programmatically controlling the input and context.
#
# For more information on the underlying tool, see the official repository:
# https://github.com/google-gemini/gemini-cli

import json
import subprocess
import sys
import os


from pipe.core.prompt_builder import PromptBuilder

from pipe.core.models.session import Session

def call_gemini_cli(settings: dict, session_data: Session, project_root: str, instruction: str, api_mode: str, multi_step_reasoning_enabled: bool, session_id: str = None) -> str:
    model_name = settings.get('model')
    if not model_name:
        raise ValueError("'model' not found in setting.yml")

    builder = PromptBuilder(settings=settings, session_data=session_data, project_root=project_root, api_mode=api_mode, multi_step_reasoning_enabled=multi_step_reasoning_enabled)
    
    final_prompt = builder.build()

    # Sanitize the prompt string to remove any surrogate characters before passing to subprocess
    final_prompt = final_prompt.encode('utf-8', 'replace').decode('utf-8')

    command = ['gemini', '-m', model_name, '--debug', '-p', final_prompt]
    if settings.get('yolo', False):
        command.insert(1, '-y')
    
    env = os.environ.copy()
    if session_id:
        env['GEMINI_SESSION_ID'] = session_id
        
    try:
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8', 
            env=env,
            bufsize=1
        )

        model_response_text = []
        for line in iter(process.stdout.readline, ''):
            print(line, end='', flush=True)
            model_response_text.append(line)
        
        process.stdout.close()
        stderr_output = process.stderr.read()
        process.stderr.close()

        return_code = process.wait()

        if return_code != 0:
            raise RuntimeError(f"Error during gemini-cli execution: {stderr_output}")
        
        if stderr_output:
            print(f"\nWarning from gemini-cli: {stderr_output}", file=sys.stderr)

        return "".join(model_response_text)
    except FileNotFoundError:
        raise RuntimeError("Error: 'gemini' command not found. Make sure it's in your PATH.")
