"""Session start action."""

from pipe.core.agents.takt_agent import TaktAgent
from pipe.core.services.session_service import SessionService
from pipe.web.action_responses import SessionStartResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.start_session import StartSessionRequest


class SessionStartAction(BaseAction):
    """Start a new session and execute an initial instruction.

    This action delegates session creation to SessionService and
    instruction execution to TaktAgent, following the DI pattern.
    """

    request_model = StartSessionRequest

    def __init__(
        self,
        session_service: SessionService,
        takt_agent: TaktAgent,
        validated_request: StartSessionRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.session_service = session_service
        self.takt_agent = takt_agent
        self.validated_request = validated_request

    def execute(self) -> SessionStartResponse:
        if not self.validated_request:
            raise ValueError("Request is required")

        request_data = self.validated_request

        # Create new session via service
        session = self.session_service.create_new_session(
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

        # Run instruction on the newly created session via TaktAgent
        self.takt_agent.run_existing_session(
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
