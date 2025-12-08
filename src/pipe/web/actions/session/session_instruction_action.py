"""Session instruction action."""

import json

from flask import Response, stream_with_context
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.send_instruction import SendInstructionRequest


class SessionInstructionAction(BaseAction):
    request_model = SendInstructionRequest

    def execute(self) -> Response:
        """
        Returns a Flask Response object with streaming content.
        This action is special and should be handled by streaming_dispatcher.
        """
        from pipe.core.agents.takt_agent import TaktAgent
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        session_service = get_session_service()
        session_data = session_service.get_session(request.session_id)
        takt_agent = TaktAgent(session_service.project_root)

        def generate():
            try:
                for line in takt_agent.run_instruction_stream_unified(
                    session_id=request.session_id,
                    instruction=request.instruction,
                    multi_step_reasoning=session_data.multi_step_reasoning_enabled,
                ):
                    yield f"data: {json.dumps({'content': line})}\n\n"
            except (RuntimeError, Exception) as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()), mimetype="text/event-stream"
        )
