"""Session turns get action."""

from pipe.web.action_responses import SessionTurnsResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.get_turns import GetTurnsRequest


class SessionTurnsGetAction(BaseAction):
    request_model = GetTurnsRequest

    def execute(self) -> SessionTurnsResponse:
        from pipe.web.service_container import get_session_turn_service

        request = self.validated_request

        turns = get_session_turn_service().get_turns(request.session_id)

        # Assuming service returns list[Turn] models (or compatible dicts)
        # SessionTurnsResponse(turns=turns) will validate/convert
        return SessionTurnsResponse(turns=turns)
