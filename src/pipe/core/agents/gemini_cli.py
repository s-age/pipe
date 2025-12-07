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
import sys
from typing import TYPE_CHECKING

from pipe.core.agents import register_agent
from pipe.core.agents.base import BaseAgent
from pipe.core.models.args import TaktArgs

if TYPE_CHECKING:
    from pipe.core.services.prompt_service import PromptService
    from pipe.core.services.session_service import SessionService


def call_gemini_cli(
    session_service: "SessionService", output_format: str = "json"
) -> dict:
    # Import here to avoid circular dependency
    from pipe.core.factories.service_factory import ServiceFactory

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

    if output_format == "stream-json":
        # For stream-json, stream the output in real-time
        command = ["gemini", "-y", "-m", model_name, "-o", output_format, "-p", "-"]
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        if session_service.current_session_id:
            env["PIPE_SESSION_ID"] = session_service.current_session_id

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

        if process.stdin:
            process.stdin.write(pretty_printed_prompt)
        if process.stdin:
            process.stdin.close()

        full_response = ""
        assistant_content = ""
        while True:
            if not process.stdout:
                break
            line = process.stdout.readline()
            if not line:
                break
            print(line.strip())
            full_response += line
            try:
                data = json.loads(line.strip())
                if data.get("type") == "message" and data.get("role") == "assistant":
                    assistant_content += data.get("content", "")
            except json.JSONDecodeError:
                pass

        stderr_output = ""
        if process.stderr:
            stderr_output = process.stderr.read()
        return_code = process.wait()
        if return_code != 0:
            raise RuntimeError(f"Error during gemini-cli execution: {stderr_output}")

        # For stream-json, parse the final result if possible
        try:
            lines = full_response.strip().split("\n")
            for line in reversed(lines):
                try:
                    result = json.loads(line)
                    if result.get("type") == "result":
                        return {
                            "response": assistant_content,
                            "stats": result.get("stats"),
                        }
                except json.JSONDecodeError:
                    continue
            return {"response": assistant_content, "stats": None}
        except json.JSONDecodeError:
            return {"response": assistant_content, "stats": None}
    else:
        # Original logic for json and text
        # Avoid passing a very large prompt as a single argv element (can hit
        # the system ARG_MAX / Argument list too long). Try streaming the prompt
        # via stdin first (many CLIs accept '-' to mean read from stdin). If
        # that fails, fall back to writing the prompt to a temporary file and
        # passing the filename.
        command = ["gemini", "-y", "-m", model_name, "-o", output_format, "-p", "-"]

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
                    stdout, stderr = process.communicate(
                        pretty_printed_prompt, timeout=60
                    )
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    raise RuntimeError(
                        "gemini-cli timed out when streaming prompt via stdin"
                    )

                return_code = process.returncode

                if return_code == 0:
                    if output_format == "text":
                        print("DEBUG: gemini(stdin) completed", file=sys.stderr)
                    try:
                        result = json.loads(stdout)
                        return result
                    except json.JSONDecodeError:
                        return {"response": stdout, "stats": None}
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

                command_file = [
                    "gemini",
                    "-y",
                    "-m",
                    model_name,
                    "-o",
                    output_format,
                    "-p",
                    tmp_path,
                ]
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
                        f"Error during gemini-cli execution: "
                        f"{last_error or stderr_output}"
                    )

                try:
                    result = json.loads(full_response)
                    return result
                except json.JSONDecodeError:
                    return {"response": full_response, "stats": None}
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


@register_agent("gemini-cli")
class GeminiCliAgent(BaseAgent):
    """Agent for Gemini CLI mode."""

    def run(
        self,
        args: TaktArgs,
        session_service: "SessionService",
        prompt_service: "PromptService",
    ) -> tuple[str, int | None, list]:
        """Execute the Gemini CLI agent.

        Args:
            args: Command line arguments
            session_service: Service for session management
            prompt_service: Service for prompt building

        Returns:
            Tuple of (response_text, token_count, turns_to_save)
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_cli_delegate
        from pipe.core.models.turn import ModelResponseTurn
        from pipe.core.utils.datetime import get_current_timestamp

        # Explicitly merge any tool calls from the pool into the main turns history
        # before calling the agent.
        session_id = session_service.current_session_id
        session_service.merge_pool_into_turns(session_id)

        model_response_text, token_count = gemini_cli_delegate.run(
            args, session_service
        )

        if args.output_format == "text":
            print(model_response_text)
        elif args.output_format == "stream-json":
            # For stream-json, the output is already streamed by gemini_cli_delegate
            pass

        final_turn = ModelResponseTurn(
            type="model_response",
            content=model_response_text,
            timestamp=get_current_timestamp(session_service.timezone_obj),
        )
        turns_to_save = [final_turn]

        return model_response_text, token_count, turns_to_save
