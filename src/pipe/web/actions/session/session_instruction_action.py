"""Session instruction action."""

import json
import logging

from flask import Response, stream_with_context
from pipe.core.services.session_instruction_service import SessionInstructionService
from pipe.core.services.session_service import SessionService
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest

logger = logging.getLogger(__name__)


class SessionInstructionAction(BaseAction):
    """Execute an instruction on a session with streaming output.

    This action delegates all subprocess management and streaming logic
    to SessionInstructionService, following the DI pattern.
    """

    request_model = SendInstructionRequest

    def __init__(
        self,
        session_service: SessionService,
        session_instruction_service: SessionInstructionService,
        validated_request: SendInstructionRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.session_service = session_service
        self.session_instruction_service = session_instruction_service
        self.validated_request = validated_request

    def execute(self) -> Response:
        """Returns a Flask Response object with streaming content."""
        request = self.validated_request

        if not request:

            def error_response():
                yield (
                    f"data: {json.dumps({'error': 'Internal Error (Request Missing)'}, ensure_ascii=False)}"
                    "\n\n"
                )

            return Response(error_response(), mimetype="text/event-stream")

        session_id = request.session_id
        session_data = self.session_service.get_session(session_id)

        if not session_data:

            def error_response():
                yield f"data: {json.dumps({'error': 'Session not found'}, ensure_ascii=False)}\n\n"

            return Response(error_response(), mimetype="text/event-stream")

        def generate():
            # Delegate to service for instruction execution
            for data in self.session_instruction_service.execute_instruction_stream(
                session_data, request.instruction
            ):
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        return Response(stream_with_context(generate()), mimetype="text/event-stream")
