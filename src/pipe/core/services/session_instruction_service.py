"""Service for executing instructions on sessions with subprocess management.

This service handles the infrastructure logic for running instructions via subprocess,
including process management, output streaming, and error handling.
"""

import json
import logging
import os
import subprocess
import sys
from collections.abc import Generator

from pipe.core.models.session import Session
from pipe.core.services.process_manager_service import ProcessManagerService

logger = logging.getLogger(__name__)


class SessionInstructionService:
    """Service for executing instructions on sessions via subprocess."""

    def __init__(self, project_root: str, settings):
        """Initialize with dependencies.

        Args:
            project_root: Project root directory
            settings: Application settings
        """
        self.project_root = project_root
        self.settings = settings

    def execute_instruction_stream(
        self, session: Session, instruction: str
    ) -> Generator[dict, None, None]:
        """Execute an instruction on a session with streaming output.

        Args:
            session: Session to execute the instruction on
            instruction: Instruction to execute

        Yields:
            Dictionaries containing streaming events/data

        Note:
            - Manages subprocess directly for better control
            - Checks if session is already running before starting
            - Automatically handles errors and cleanup
            - Streams output as JSON events
        """
        session_id = session.session_id
        process_manager = ProcessManagerService(self.project_root)

        # Check if session is already running
        if process_manager.is_running(session_id):
            logger.warning(f"Session {session_id} is already running")
            yield {
                "error": f"Session {session_id} is already running. "
                "Please wait for the current instruction to complete or stop it first."
            }
            return

        process = None
        try:
            # Initial event
            yield {"type": "start", "session_id": session_id}

            # Build command for subprocess
            command = [
                sys.executable,
                "-m",
                "pipe.cli.takt",
                "--session",
                session_id,
                "--instruction",
                instruction,
                "--output-format",
                "stream-json",
            ]

            if session.multi_step_reasoning_enabled:
                command.append("--multi-step-reasoning")

            # Start subprocess with Popen
            # Note: Process registration is handled inside takt CLI (_dispatch_run)
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                bufsize=1,
                cwd=self.project_root,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )

            # Check if process is still running before reading
            poll_result = process.poll()
            if poll_result is not None:
                # Process already exited
                stderr_output = ""
                if process.stderr:
                    stderr_output = process.stderr.read()
                yield {"error": f"Process exited unexpectedly: {stderr_output}"}
                return

            # Stream output from subprocess
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    if line:
                        # Parse JSON output from takt CLI
                        try:
                            data = json.loads(line.strip())
                            yield data
                        except json.JSONDecodeError:
                            # If not JSON, wrap it as content
                            yield {"content": line.strip()}

                process.stdout.close()

            # Wait for process to complete
            return_code = process.wait()

            if return_code != 0:
                # Process failed
                stderr_output = ""
                if process.stderr:
                    stderr_output = process.stderr.read()
                    process.stderr.close()

                error_msg = f"Process failed with code {return_code}: {stderr_output}"
                logger.error(error_msg)
                yield {"error": error_msg}

        except Exception as e:
            logger.error(f"Exception in session instruction streaming: {e}")
            yield {"error": str(e)}

        finally:
            # Cleanup process
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()

            # Note: Process cleanup is handled inside takt CLI's finally block
