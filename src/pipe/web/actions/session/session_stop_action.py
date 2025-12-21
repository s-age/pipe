"""Session stop action."""

from pipe.core.services.session_service import SessionService
from pipe.core.services.session_workflow_service import SessionWorkflowService
from pipe.web.action_responses import SessionStopResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.stop_session import StopSessionRequest


class SessionStopAction(BaseAction):
    """Stops a running session by killing process and rolling back transaction.

    Delegates all stop logic to SessionWorkflowService, following the DI pattern.
    """

    request_model = StopSessionRequest

    def __init__(
        self,
        session_service: SessionService,
        session_workflow_service: SessionWorkflowService,
        validated_request: StopSessionRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.session_service = session_service
        self.session_workflow_service = session_workflow_service
        self.validated_request = validated_request

    def execute(self) -> SessionStopResponse:
        if not self.validated_request:
            raise ValueError("Request is required")

        request = self.validated_request
        session_id = request.session_id

        # Delegate to workflow service for all stop logic
        self.session_workflow_service.stop_session(
            session_id, self.session_service.project_root
        )

        return SessionStopResponse(
            message=f"Session {session_id} stopped and transaction rolled back.",
            session_id=session_id,
        )
