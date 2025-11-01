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

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.services.session_service import SessionService


def call_gemini_cli(session_service: SessionService) -> str:
    settings = session_service.settings
    project_root = session_service.project_root

    model_name = settings.model
    if not model_name:
        raise ValueError("'model' not found in settings")

    service_factory = ServiceFactory(project_root, settings)
    prompt_service = service_factory.create_prompt_service()
    prompt_model = prompt_service.build_prompt(session_service)

    # Render the prompt using the appropriate template
    template_name = (
        "gemini_api_prompt.j2"
        if settings.api_mode == "gemini-api"
        else "gemini_cli_prompt.j2"
    )
    template = prompt_service.jinja_env.get_template(template_name)
    rendered_prompt = template.render(session=prompt_model)

    # Ensure the rendered prompt is valid JSON and pretty-print it
    pretty_printed_prompt = json.dumps(json.loads(rendered_prompt), indent=2)

    command = [
        "gemini",
        "-y",
        "-m",
        model_name,
        "-p",
        pretty_printed_prompt,
    ]

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )

        full_response = ""
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                full_response += line

        stderr_output = ""
        if process.stderr:
            stderr_output = process.stderr.read()

        return_code = process.wait()

        if return_code != 0:
            raise RuntimeError(f"Error during gemini-cli execution: {stderr_output}")

        return full_response
    except FileNotFoundError:
        raise RuntimeError(
            "Error: 'gemini' command not found. "
            "Please ensure it is installed and in your PATH."
        )
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
