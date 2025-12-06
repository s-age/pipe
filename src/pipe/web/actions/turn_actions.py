from typing import Any

from pipe.web.actions.base_action import BaseAction


class SessionTurnsGetAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            since_index = int(self.params.get("since", 0))
            session_data = get_session_service().get_session(session_id)
            if not session_data:
                return {"message": "Session not found."}, 404

            all_turns = [turn.model_dump() for turn in session_data.turns]
            new_turns = all_turns[since_index:]

            return {"turns": new_turns}, 200
        except Exception as e:
            return {"message": str(e)}, 500


class TurnDeleteAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        turn_index = self.params.get("turn_index")

        if not session_id or turn_index is None:
            return {"message": "session_id and turn_index are required"}, 400

        try:
            turn_index = int(turn_index)
        except ValueError:
            return {"message": "turn_index must be an integer"}, 400

        try:
            get_session_service().delete_turn(session_id, turn_index)
            return {
                "message": f"Turn {turn_index} from session {session_id} deleted.",
            }, 200
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except IndexError:
            return {"message": "Turn index out of range."}, 400
        except Exception as e:
            return {"message": str(e)}, 500


class TurnEditAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.requests.sessions.edit_turn import EditTurnRequest
        from pipe.web.service_container import get_session_service
        from pydantic import ValidationError

        session_id = self.params.get("session_id")
        turn_index = self.params.get("turn_index")

        if not session_id or turn_index is None:
            return {"message": "session_id and turn_index are required"}, 400

        try:
            turn_index = int(turn_index)
        except ValueError:
            return {"message": "turn_index must be an integer"}, 400

        try:
            new_data = self.request_data.get_json()
            if not new_data:
                return {"message": "No data provided."}, 400

            # Validate request using Pydantic model
            try:
                edit_request = EditTurnRequest(**new_data)
                validated_data = edit_request.model_dump()
            except ValidationError as e:
                error_messages = [err["msg"] for err in e.errors()]
                return {"message": "; ".join(error_messages)}, 400

            get_session_service().edit_turn(session_id, turn_index, validated_data)
            return {
                "message": f"Turn {turn_index + 1} from session {session_id} updated.",
            }, 200
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except IndexError:
            return {"message": "Turn index out of range."}, 400
        except ValueError as e:
            return {"message": str(e)}, 403
        except Exception as e:
            return {"message": str(e)}, 500
