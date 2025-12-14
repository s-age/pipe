"""Session start action."""

from flask import Request
from pipe.web.action_responses import SessionStartResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.start_session import StartSessionRequest


class SessionStartAction(BaseAction):
    request_model = StartSessionRequest

    def __init__(
        self,
        validated_request: StartSessionRequest | None = None,
        params: dict | None = None,
        request_data: Request | None = None,
        **kwargs,
    ):
        super().__init__(params, request_data, **kwargs)
        self.validated_request = validated_request

    def execute(self) -> SessionStartResponse:
        if not self.validated_request:
            raise ValueError("Request is required")

        from pipe.core.agents.takt_agent import TaktAgent
        from pipe.web.service_container import get_session_service

        request_data = self.validated_request

        session = get_session_service().create_new_session(
            purpose=request_data.purpose,
            background=request_data.background,
            roles=request_data.roles,
            multi_step_reasoning_enabled=request_data.multi_step_reasoning_enabled,
            hyperparameters=request_data.hyperparameters,
            parent_id=request_data.parent,
            artifacts=request_data.artifacts,
            procedure=request_data.procedure,
        )
        session_id = session.session_id

        session_service = get_session_service()
        takt_agent = TaktAgent(session_service.project_root)

        # Run instruction on the newly created session
        takt_agent.run_existing_session(
            session_id=session_id,
            instruction=request_data.instruction,
            output_format="stream-json",
            multi_step_reasoning=request_data.multi_step_reasoning_enabled,
            references=(
                [r.path for r in request_data.references]
                if request_data.references
                else None
            ),
            artifacts=request_data.artifacts,
            procedure=request_data.procedure,
        )

        return SessionStartResponse(session_id=session_id)
