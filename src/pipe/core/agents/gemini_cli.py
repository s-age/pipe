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

    model_name = settings.model.name
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
        # Pass GOOGLE_API_KEY as GEMINI_API_KEY for gemini-cli
        if "GOOGLE_API_KEY" in os.environ:
            env["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

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
        tool_calls = []  # Store tool_use events
        tool_results = []  # Store tool_result events

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
                elif data.get("type") == "tool_use":
                    # Store tool call for later processing
                    tool_calls.append(data)
                elif data.get("type") == "tool_result":
                    # Store tool result for later processing
                    tool_results.append(data)
            except json.JSONDecodeError:
                pass

        stderr_output = ""
        if process.stderr:
            stderr_output = process.stderr.read()
        return_code = process.wait()
        if return_code != 0:
            raise RuntimeError(f"Error during gemini-cli execution: {stderr_output}")

        # Save tool calls and results to session pool
        # Only save if pools is empty (standard tools)
        # Skip if mcp_server already saved (pipe_tools)
        if tool_calls or tool_results:
            from pipe.core.models.turn import (
                FunctionCallingTurn,
                ToolResponseTurn,
                TurnResponse,
            )
            from pipe.core.utils.datetime import get_current_timestamp

            session_id = session_service.current_session_id

            # Reload session to check if mcp_server.py added tools to pools
            session = session_service.repository.find(session_id)
            if session:
                # Only add to pools if it's empty (standard tools)
                # If pools has data, mcp_server.py recorded pipe_tools
                if len(session.pools) == 0:
                    for tool_call in tool_calls:
                        # Create FunctionCallingTurn
                        tool_name = tool_call.get("tool_name", "")
                        parameters = tool_call.get("parameters", {})
                        # Format as function call string
                        params_json = json.dumps(parameters, ensure_ascii=False)
                        response_str = f"{tool_name}({params_json})"
                        timestamp = tool_call.get(
                            "timestamp",
                            get_current_timestamp(session_service.timezone_obj),
                        )
                        turn = FunctionCallingTurn(
                            type="function_calling",
                            response=response_str,
                            timestamp=timestamp,
                        )
                        session.pools.append(turn)

                    for tool_result in tool_results:
                        # Create ToolResponseTurn
                        # Extract tool name from tool_id
                        tool_name = tool_result.get("tool_id", "").split("-")[0]
                        status = tool_result.get("status", "failed")
                        output = tool_result.get("output", "")
                        error = tool_result.get("error")

                        # Create TurnResponse
                        if status == "success":
                            response = TurnResponse(
                                status="succeeded",
                                message=output,
                            )
                        else:
                            if isinstance(error, dict):
                                error_msg = error.get("message", "")
                            else:
                                error_msg = str(error)
                            response = TurnResponse(
                                status="failed",
                                message=error_msg,
                            )

                        timestamp = tool_result.get(
                            "timestamp",
                            get_current_timestamp(session_service.timezone_obj),
                        )
                        turn = ToolResponseTurn(
                            type="tool_response",
                            name=tool_name,
                            response=response,
                            timestamp=timestamp,
                        )
                        session.pools.append(turn)

                    # Save updated session
                    session_service.repository.save(session)

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
                            "tool_calls": tool_calls,
                            "tool_results": tool_results,
                        }
                except json.JSONDecodeError:
                    continue
            return {
                "response": assistant_content,
                "stats": None,
                "tool_calls": tool_calls,
                "tool_results": tool_results,
            }
        except json.JSONDecodeError:
            return {
                "response": assistant_content,
                "stats": None,
                "tool_calls": tool_calls,
                "tool_results": tool_results,
            }
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
        # Pass GOOGLE_API_KEY as GEMINI_API_KEY for gemini-cli
        if "GOOGLE_API_KEY" in os.environ:
            env["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

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
                    # 300 seconds (5 minutes) to allow for complex compression
                    stdout, stderr = process.communicate(
                        pretty_printed_prompt, timeout=900
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
    ) -> tuple[str, int | None, list, str | None]:
        """Execute the Gemini CLI agent.

        Args:
            args: Command line arguments
            session_service: Service for session management
            prompt_service: Service for prompt building

        Returns:
            Tuple of (response_text, token_count, turns_to_save, thought_text)
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_cli_delegate
        from pipe.core.models.turn import ModelResponseTurn
        from pipe.core.services.session_turn_service import SessionTurnService
        from pipe.core.utils.datetime import get_current_timestamp

        # Explicitly merge any tool calls from the pool into the main turns history
        # before calling the agent.
        session_id = session_service.current_session_id
        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )
        session_turn_service.merge_pool_into_turns(session_id)

        model_response_text, token_count = gemini_cli_delegate.run(
            args, session_service, session_turn_service
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

        return model_response_text, token_count, turns_to_save, None
