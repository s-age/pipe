"""Turn edit action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_turn import EditTurnRequest


class TurnEditAction(BaseAction):
    request_model = EditTurnRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_turn_service

        request = self.validated_request
        validated_data = request.model_dump(exclude={"session_id", "turn_index"})
        get_session_turn_service().edit_turn(
            request.session_id, request.turn_index, validated_data
        )

        return {
            "message": (
                f"Turn {request.turn_index + 1} from session "
                f"{request.session_id} updated."
            )
        }
