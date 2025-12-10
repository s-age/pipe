"""Session instruction action."""

import json
import logging
import os
import subprocess
import sys

from flask import Response, stream_with_context
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest

logger = logging.getLogger(__name__)


class SessionInstructionAction(BaseAction):
    """
    Execute an instruction on a session with process management.

    Flow:
    1. Check if session is already running (concurrent execution prevention)
    2. Start subprocess via Popen
    3. Register process in ProcessManager
    4. Stream output from subprocess
    5. Handle errors and cleanup

    Note:
    - Uses Popen for subprocess control and process registration
    - Automatically rolls back transaction on error
    """

    request_model = SendInstructionRequest

    def execute(self) -> Response:
        """
        Returns a Flask Response object with streaming content.
        """

        from pipe.web.service_container import get_session_service

        request = self.validated_request

        if not request:

            def error_response():
                yield (
                    f"data: {json.dumps({'error': 'Internal Error (Request Missing)'})}"
                    "\n\n"
                )

            return Response(error_response(), mimetype="text/event-stream")

        session_service = get_session_service()
        session_id = request.session_id
        session_data = session_service.get_session(session_id)

        if not session_data:

            def error_response():
                yield f"data: {json.dumps({'error': 'Session not found'})}\n\n"

            return Response(error_response(), mimetype="text/event-stream")

        def generate():
            process = None
            try:
                # Build command for subprocess
                command = [
                    sys.executable,
                    "-m",
                    "pipe.cli.takt",
                    "--session",
                    session_id,
                    "--instruction",
                    request.instruction,
                    "--output-format",
                    "stream-json",
                ]

                if session_data.multi_step_reasoning_enabled:
                    command.append("--multi-step-reasoning")

                # Start subprocess with Popen
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    bufsize=1,
                    cwd=session_service.project_root,
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                )

                # Check if process is still running before reading
                poll_result = process.poll()
                if poll_result is not None:
                    # Process already exited
                    stderr_output = ""
                    if process.stderr:
                        stderr_output = process.stderr.read()
                    yield (f"data: {json.dumps({'error': 'Process exited'})}\n\n")
                    return

                # Test: yield initial event
                event_data = {"type": "start", "session_id": session_id}
                yield f"data: {json.dumps(event_data)}\n\n"

                # Stream output from subprocess
                if process.stdout:
                    for line in iter(process.stdout.readline, ""):
                        if line:
                            # Parse JSON output from takt CLI
                            try:
                                data = json.loads(line.strip())
                                yield f"data: {json.dumps(data)}\n\n"
                            except json.JSONDecodeError:
                                # If not JSON, wrap it as content
                                yield (
                                    f"data: {json.dumps({'content': line.strip()})}"
                                    "\n\n"
                                )

                    process.stdout.close()

                # Wait for process to complete
                return_code = process.wait()

                if return_code != 0:
                    # Process failed - transaction should be rolled back by dispatcher
                    stderr_output = ""
                    if process.stderr:
                        stderr_output = process.stderr.read()
                        process.stderr.close()

                    error_msg = f"Process failed: {stderr_output}"
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"

            except Exception as e:
                logger.error(f"Exception in session instruction streaming: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            finally:
                # Cleanup process
                if process and process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()

        return Response(stream_with_context(generate()), mimetype="text/event-stream")
