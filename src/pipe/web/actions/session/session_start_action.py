"""Session start action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.start_session import StartSessionRequest


class SessionStartAction(BaseAction):
    body_model = StartSessionRequest  # Legacy pattern: no path params

    def execute(self) -> dict[str, str]:
        from pipe.core.agents.takt_agent import TaktAgent
        from pipe.web.service_container import get_session_service

        request_data = StartSessionRequest(**self.request_data.get_json())

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

        return {"session_id": session_id}
