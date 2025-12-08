"""Session turns get action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.get_turns import GetTurnsRequest


class SessionTurnsGetAction(BaseAction):
    request_model = GetTurnsRequest

    def execute(self) -> dict[str, list[dict]]:
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        session_data = get_session_service().get_session(request.session_id)
        turns = session_data.turns[request.since:]
        return {"turns": [turn.model_dump() for turn in turns]}
