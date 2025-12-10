"""Turn delete action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.delete_turn import DeleteTurnRequest


class TurnDeleteAction(BaseAction):
    request_model = DeleteTurnRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_turn_service

        request = self.validated_request
        get_session_turn_service().delete_turn(request.session_id, request.turn_index)
        return {
            "message": (
                f"Turn {request.turn_index} from session "
                f"{request.session_id} deleted."
            )
        }
