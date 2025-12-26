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
) -> dict:
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
                        session_service=session_service,
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

                    # Save tool results to session pool
                    stream_processor.save_tool_results_to_pool()

                    # Return the collected result
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

        # Explicitly merge any tool calls from the pool into the main turns history
        # before calling the agent.
        session_id = session_service.current_session_id
        session_turn_service = SessionTurnService(
            session_service.settings, session_service.repository
        )
        session_turn_service.merge_pool_into_turns(session_id)

        model_response_text, token_count, stats = gemini_cli_delegate.run(
            args, session_service, session_turn_service
        )

        # Update cumulative token stats in session
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
