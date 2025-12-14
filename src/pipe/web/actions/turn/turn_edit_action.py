"""Turn edit action."""

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_turn import EditTurnRequest


class TurnEditAction(BaseAction):
    request_model = EditTurnRequest

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_session_turn_service

        request = self.validated_request

        # Extract update data excluding path params and None values
        new_turn_data = request.model_dump(
            exclude={"session_id", "turn_index"}, exclude_none=True
        )

        get_session_turn_service().edit_turn(
            request.session_id, request.turn_index, new_turn_data
        )

        return SuccessMessageResponse(message="Turn updated successfully")
