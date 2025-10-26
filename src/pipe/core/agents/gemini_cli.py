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
from jinja2 import Environment, FileSystemLoader

from pipe.core.services.session_service import SessionService
from pipe.core.services.prompt_service import PromptService

def call_gemini_cli(session_service: SessionService) -> str:
    settings = session_service.settings
    session_data = session_service.current_session
    project_root = session_service.project_root
    session_id = session_service.current_session_id
    multi_step_reasoning_enabled = session_data.multi_step_reasoning_enabled
    
    model_name = settings.model
    if not model_name:
        raise ValueError("'model' not found in settings")

    prompt_service = PromptService(project_root)
    prompt_model = prompt_service.build_prompt(session_service)

    template_env = Environment(
        loader=FileSystemLoader(os.path.join(project_root, 'templates', 'prompt')),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = template_env.get_template('gemini_cli_prompt.j2')
    
    context = prompt_model.model_dump()
    final_prompt = template.render(session=context)

    # Sanitize the prompt string to remove any surrogate characters before passing to subprocess
    final_prompt = final_prompt.encode('utf-8', 'replace').decode('utf-8')

    command = ['gemini', '-m', model_name, '--debug', '-p', final_prompt]
    if settings.yolo:
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
