"""Turn delete action."""

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_turn import DeleteTurnRequest


class TurnDeleteAction(BaseAction):
    request_model = DeleteTurnRequest

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_session_turn_service

        request = self.validated_request

        get_session_turn_service().delete_turn(request.session_id, request.turn_index)

        return SuccessMessageResponse(message="Turn deleted successfully")
