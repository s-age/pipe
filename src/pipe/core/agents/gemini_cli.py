# This script acts as a wrapper for the official Google Gemini CLI tool.
# It handles the execution of the 'gemini' command-line tool as a subprocess.
#
# Responsibilities:
# - gemini_cli_payload.py: Constructs the JSON prompt payload
# - gemini_cli_stream_processor.py: Processes streaming JSON output and manages logs
# - This file: Manages subprocess communication and coordination
#
# For more information on the underlying tool, see the official repository:
# https://github.com/google-gemini/gemini-cli

import json
import os
import subprocess
from typing import TYPE_CHECKING

from pipe.core.agents import register_agent
from pipe.core.agents.base import BaseAgent
from pipe.core.models.args import TaktArgs

if TYPE_CHECKING:
    from pipe.core.services.session_service import SessionService


def call_gemini_cli(
    session_service: "SessionService",
    output_format: str = "json",
    prompt: str | None = None,
):
    # Import here to avoid circular dependency
    from pipe.core.domains.gemini_cli_payload import GeminiCliPayloadBuilder
    from pipe.core.repositories.streaming_log_repository import StreamingLogRepository

    settings = session_service.settings
    project_root = session_service.project_root

    # Initialize streaming log repository for tee-style logging
    streaming_log_repo = None
    if session_service.current_session_id:
        streaming_log_repo = StreamingLogRepository(
            project_root=project_root,
            session_id=session_service.current_session_id,
            settings=settings,
        )

    model_name = settings.model.name
    if not model_name:
        raise ValueError("'model' not found in settings")

    # Use provided prompt or build it internally
    if prompt is not None:
        pretty_printed_prompt = prompt
    else:
        # Build prompt using the new payload builder (bypasses PromptService)
        payload_builder = GeminiCliPayloadBuilder(
            project_root=project_root,
            api_mode=settings.api_mode,
        )
        pretty_printed_prompt = payload_builder.build(session_service)

    # Use a temporary file to pass the prompt to gemini-cli.
    # We pipe this file directly to stdin to avoid buffer issues and argument limits.
    import tempfile

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, encoding="utf-8"
        ) as tf:
            tf.write(pretty_printed_prompt)
            tmp_path = tf.name

        # Use '-' to tell gemini to read from stdin
        command = [
            "gemini",
            "-y",
            "-m",
            model_name,
            "-o",
            output_format,
            "-p",
            "-",
        ]

        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        if session_service.current_session_id:
            env["PIPE_SESSION_ID"] = session_service.current_session_id
        # Pass GOOGLE_API_KEY as GEMINI_API_KEY for gemini-cli
        if "GOOGLE_API_KEY" in os.environ:
            env["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

        with open(tmp_path, encoding="utf-8") as stdin_f:
            # Unified subprocess launch logic
            try:
                process = subprocess.Popen(
                    command,
                    stdin=stdin_f,  # Direct file pipe
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    env=env,
                    bufsize=1,
                )
            except FileNotFoundError:
                raise RuntimeError(
                    "Error: 'gemini' command not found. "
                    "Please ensure it is installed and in your PATH."
                )

            # Handle output based on format
            try:
                if output_format == "stream-json":
                    # For stream-json, stream the output in real-time
                    from pipe.core.domains.gemini_cli_stream_processor import (
                        GeminiCliStreamProcessor,
                    )

                    # Use the stream processor to handle JSON parsing and logging
                    stream_processor = GeminiCliStreamProcessor(
                        streaming_log_repo=streaming_log_repo,
                    )

                    while True:
                        if not process.stdout:
                            break
                        line = process.stdout.readline()
                        if not line:
                            break
                        stream_processor.process_line(line)

                    stderr_output = ""
                    if process.stderr:
                        stderr_output = process.stderr.read()
                    return_code = process.wait()
                    if return_code != 0:
                        raise RuntimeError(
                            f"Error during gemini-cli execution: {stderr_output}"
                        )

                    # Return the collected result (no persistence here)
                    return stream_processor.get_result()

                else:
                    # Original logic for json and text
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
                            f"Error during gemini-cli execution: {stderr_output}"
                        )

                    try:
                        result = json.loads(full_response)
                        return result
                    except json.JSONDecodeError:
                        return {"response": full_response, "stats": None}

            except Exception as e:
                if "gemini" in str(e) and "not found" in str(e):
                    raise
                raise RuntimeError(f"An unexpected error occurred: {e}")

    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


@register_agent("gemini-cli")
class GeminiCliAgent(BaseAgent):
    """Agent for Gemini CLI mode."""

    def __init__(self, session_service: "SessionService"):
        """Initialize the Gemini CLI agent.

        Args:
            session_service: Session service for accessing session data and settings
        """
        self.session_service = session_service

    def run(
        self,
        args: TaktArgs,
        session_service: "SessionService",
    ) -> tuple[str, int | None, list, str | None]:
        """Execute the Gemini CLI agent.

        Args:
            args: Command line arguments
            session_service: Service for session management

        Returns:
            Tuple of (response_text, token_count, turns_to_save, thought_text)
        """
        # Import here to avoid circular dependency
        from pipe.core.delegates import gemini_cli_delegate
        from pipe.core.models.turn import ModelResponseTurn
        from pipe.core.services.session_turn_service import SessionTurnService
        from pipe.core.utils.datetime import get_current_timestamp

        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )

        model_response_text, token_count, stats = gemini_cli_delegate.run(
            args, session_service, session_turn_service
        )

        # Update cumulative token stats in session
        session_id = session_service.current_session_id
        if stats and session_id:
            session = session_service.get_session(session_id)
            if session:
                # Add total_tokens and cached to cumulative counters
                session.cumulative_total_tokens += stats.get("total_tokens", 0)
                session.cumulative_cached_tokens += stats.get("cached", 0)
                # Save updated session
                session_service.repository.save(session)

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

    def run_stream(
        self,
        args: TaktArgs,
        session_service: "SessionService",
    ):
        """Execute the Gemini CLI agent in streaming mode.

        This method yields intermediate results for WebUI streaming support.

        Args:
            args: Command line arguments
            session_service: Service for session management

        Yields:
            Intermediate streaming results and final tuple
        """
        # Import here to avoid circular dependency
        import tempfile

        from pipe.core.domains import gemini_token_count
        from pipe.core.domains.gemini_cli_payload import GeminiCliPayloadBuilder
        from pipe.core.domains.gemini_cli_stream_processor import (
            GeminiCliStreamProcessor,
        )
        from pipe.core.models.turn import ModelResponseTurn
        from pipe.core.repositories.streaming_log_repository import (
            StreamingLogRepository,
        )
        from pipe.core.services.gemini_tool_service import GeminiToolService
        from pipe.core.services.session_turn_service import SessionTurnService
        from pipe.core.utils.datetime import get_current_timestamp

        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )

        settings = session_service.settings
        project_root = session_service.project_root
        session_id = session_service.current_session_id

        # Initialize streaming log repository
        streaming_log_repo = None
        if session_id:
            streaming_log_repo = StreamingLogRepository(
                project_root=project_root,
                session_id=session_id,
                settings=settings,
            )

        # Build prompt
        payload_builder = GeminiCliPayloadBuilder(
            project_root=project_root,
            api_mode=settings.api_mode,
        )
        rendered_prompt = payload_builder.build(session_service)

        # Calculate token count
        tool_service = GeminiToolService()
        tools = tool_service.load_tools(project_root)
        tokenizer = gemini_token_count.create_local_tokenizer(settings.model.name)
        token_count = gemini_token_count.count_tokens(
            rendered_prompt, tools=tools, tokenizer=tokenizer
        )

        # Prepare gemini-cli subprocess
        model_name = settings.model.name
        if not model_name:
            raise ValueError("'model' not found in settings")

        # Use stream-json format for streaming
        output_format = "stream-json"

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, encoding="utf-8"
            ) as tf:
                tf.write(rendered_prompt)
                tmp_path = tf.name

            command = [
                "gemini",
                "-y",
                "-m",
                model_name,
                "-o",
                output_format,
                "-p",
                "-",
            ]

            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            if session_id:
                env["PIPE_SESSION_ID"] = session_id
            if "GOOGLE_API_KEY" in os.environ:
                env["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

            with open(tmp_path, encoding="utf-8") as stdin_f:
                try:
                    process = subprocess.Popen(
                        command,
                        stdin=stdin_f,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding="utf-8",
                        env=env,
                        bufsize=1,
                    )
                except FileNotFoundError:
                    raise RuntimeError(
                        "Error: 'gemini' command not found. "
                        "Please ensure it is installed and in your PATH."
                    )

                # Stream processor to collect response
                stream_processor = GeminiCliStreamProcessor(
                    streaming_log_repo=streaming_log_repo,
                )

                # Stream output line by line
                while True:
                    if not process.stdout:
                        break
                    line = process.stdout.readline()
                    if not line:
                        break

                    # Process line (prints to stdout and logs)
                    stream_processor.process_line(line)

                    # Parse and yield assistant content chunks
                    try:
                        data = json.loads(line.strip())
                        if (
                            data.get("type") == "message"
                            and data.get("role") == "assistant"
                            and data.get("delta")
                        ):
                            content = data.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        pass

                stderr_output = ""
                if process.stderr:
                    stderr_output = process.stderr.read()
                return_code = process.wait()
                if return_code != 0:
                    raise RuntimeError(
                        f"Error during gemini-cli execution: {stderr_output}"
                    )

                # Get final result
                result = stream_processor.get_result()
                model_response_text = result.response
                stats = result.stats

                # Reconcile tool calls
                from pipe.core.delegates.gemini_cli_delegate import (
                    _reconcile_tool_calls,
                )

                if session_id:
                    session_service.current_session = session_service.get_session(
                        session_id
                    )
                    _reconcile_tool_calls(result, session_service)
                    session_turn_service.merge_pool_into_turns(session_id)

                # Update cumulative token stats
                if stats and session_id:
                    session = session_service.get_session(session_id)
                    if session:
                        session.cumulative_total_tokens += stats.get("total_tokens", 0)
                        session.cumulative_cached_tokens += stats.get("cached", 0)
                        session_service.repository.save(session)

                final_turn = ModelResponseTurn(
                    type="model_response",
                    content=model_response_text,
                    timestamp=get_current_timestamp(session_service.timezone_obj),
                )
                turns_to_save = [final_turn]

                # Yield final result with "end" marker
                yield (
                    "end",
                    model_response_text,
                    token_count,
                    turns_to_save,
                    None,
                )

        finally:
            try:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
