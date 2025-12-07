from pipe.core.models.turn import Turn
from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.edit_turn import EditTurnRequest

TurnList = list[Turn]


class SessionTurnsGetAction(BaseAction):
    def execute(self) -> dict[str, list[dict]]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            raise BadRequestError("session_id is required")

        since_index = int(self.params.get("since", 0))
        session_data = get_session_service().get_session(session_id)
        if not session_data:
            raise NotFoundError("Session not found.")

        turns = session_data.turns[since_index:]
        return {"turns": [turn.model_dump() for turn in turns]}


class TurnDeleteAction(BaseAction):
    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        turn_index = self.params.get("turn_index")

        if not session_id or turn_index is None:
            raise BadRequestError("session_id and turn_index are required")

        try:
            turn_index = int(turn_index)
        except ValueError:
            raise BadRequestError("turn_index must be an integer")

        try:
            get_session_service().delete_turn(session_id, turn_index)
            return {"message": f"Turn {turn_index} from session {session_id} deleted."}
        except FileNotFoundError:
            raise NotFoundError("Session not found.")
        except IndexError:
            raise BadRequestError("Turn index out of range.")


class TurnEditAction(BaseAction):
    request_model = EditTurnRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        turn_index = int(request.turn_index)

        validated_data = request.model_dump(exclude={"session_id", "turn_index"})

        try:
            get_session_service().edit_turn(
                request.session_id, turn_index, validated_data
            )
            return {
                "message": (
                    f"Turn {turn_index + 1} from session {request.session_id} updated."
                )
            }
        except FileNotFoundError:
            raise NotFoundError("Session not found.")
        except IndexError:
            raise BadRequestError("Turn index out of range.")
        except ValueError as e:
            from pipe.web.exceptions import InternalServerError

            raise InternalServerError(str(e))


class SessionForkAction(BaseAction):
    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        fork_index = self.params.get("fork_index")
        if fork_index is None:
            raise BadRequestError("fork_index is required")

        try:
            fork_index = int(fork_index)
        except ValueError:
            raise BadRequestError("fork_index must be an integer")

        session_id = self.params.get("session_id")
        if not session_id:
            raise BadRequestError("session_id is required")

        try:
            new_session_id = get_session_service().fork_session(session_id, fork_index)
            if new_session_id:
                return {"new_session_id": new_session_id}
            else:
                from pipe.web.exceptions import InternalServerError

                raise InternalServerError("Failed to fork session.")
        except FileNotFoundError:
            raise NotFoundError("Session not found.")
        except IndexError:
            raise BadRequestError("Fork turn index out of range.")
