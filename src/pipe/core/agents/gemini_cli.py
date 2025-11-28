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
import os
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

    # Avoid passing a very large prompt as a single argv element (can hit
    # the system ARG_MAX / Argument list too long). Try streaming the prompt
    # via stdin first (many CLIs accept '-' to mean read from stdin). If
    # that fails, fall back to writing the prompt to a temporary file and
    # passing the filename.
    command = ["gemini", "-y", "-m", model_name, "-p", "-"]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"  # Force unbuffered output for streaming
    # CRITICAL: This environment variable ensures that the Gemini CLI
    # operates within the context of the current session.
    # Do NOT remove or modify this line without careful consideration,
    # as it is essential for tools to access session-specific data.
    if session_service.current_session_id:
        env["PIPE_SESSION_ID"] = session_service.current_session_id

    try:
        # First attempt: stream prompt via stdin (using '-' with -p)
        try:
            # Debug: show we're attempting to launch gemini with stdin
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                env=env,
                bufsize=1,
            )

            try:
                # Use a timeout to avoid hanging indefinitely
                stdout, stderr = process.communicate(pretty_printed_prompt, timeout=60)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                raise RuntimeError(
                    "gemini-cli timed out when streaming prompt via stdin"
                )

            return_code = process.returncode

            if return_code == 0:
                print("DEBUG: gemini(stdin) completed successfully")
                return stdout
            # If non-zero, fall through to fallback below and include stderr
            last_error = stderr
        except OSError as e:
            # Could be "Argument list too long" or other exec issues.
            last_error = str(e)

        # Fallback: write prompt to a temporary file and pass filename
        import tempfile

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as tf:
                tf.write(pretty_printed_prompt)
                tmp_path = tf.name

            command_file = ["gemini", "-y", "-m", model_name, "-p", tmp_path]
            process = subprocess.Popen(
                command_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                env=env,
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
                raise RuntimeError(
                    f"Error during gemini-cli execution: {last_error or stderr_output}"
                )

            return full_response
        finally:
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
    except FileNotFoundError:
        raise RuntimeError(
            "Error: 'gemini' command not found. "
            "Please ensure it is installed and in your PATH."
        )
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
