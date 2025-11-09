from typing import Any

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_hyperparameters import EditHyperparametersRequest
from pipe.web.requests.sessions.edit_multi_step_reasoning import (
    EditMultiStepReasoningRequest,
)
from pipe.web.requests.sessions.edit_session_meta import EditSessionMetaRequest
from pipe.web.requests.sessions.edit_todos import EditTodosRequest
from pydantic import ValidationError


class SessionMetaEditAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            request_data = EditSessionMetaRequest(**self.request_data.get_json())
            session_service.edit_session_meta(
                session_id, request_data.model_dump(exclude_unset=True)
            )
            return {"message": f"Session {session_id} metadata updated."}, 200
        except ValidationError as e:
            return {"message": str(e)}, 422
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except Exception as e:
            return {"message": str(e)}, 500


class HyperparametersEditAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            try:
                request_data = EditHyperparametersRequest(
                    **self.request_data.get_json()
                )
            except ValidationError as e:
                return {"message": str(e)}, 422
            except Exception:
                return {"message": "No data provided."}, 400

            hyperparams = request_data.model_dump(exclude_unset=True)
            session_service.edit_session_meta(
                session_id, {"hyperparameters": hyperparams}
            )

            session = session_service.get_session(session_id)
            if not session:
                return {"message": "Session not found."}, 404

            return {
                "message": f"Session {session_id} hyperparameters updated.",
                "session": session.to_dict(),
            }, 200
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except Exception as e:
            return {"message": str(e)}, 500


class MultiStepReasoningEditAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            try:
                request_data = EditMultiStepReasoningRequest(
                    **self.request_data.get_json()
                )
            except ValidationError as e:
                return {"message": str(e)}, 422
            except Exception:
                return {"message": "No data provided."}, 400

            session_service.edit_session_meta(
                session_id,
                {
                    "multi_step_reasoning_enabled": (
                        request_data.multi_step_reasoning_enabled
                    )
                },
            )

            session = session_service.get_session(session_id)
            if not session:
                return {"message": "Session not found."}, 404

            return {
                "message": f"Session {session_id} multi-step reasoning updated.",
                "session": session.to_dict(),
            }, 200
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except Exception as e:
            return {"message": str(e)}, 500


class TodosEditAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            request_data = EditTodosRequest(**self.request_data.get_json())
            session_service.update_todos(session_id, request_data.todos)
            return {"message": f"Session {session_id} todos updated."}, 200
        except ValidationError as e:
            return {"message": str(e)}, 422
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except Exception as e:
            return {"message": str(e)}, 500


class TodosDeleteAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.app import session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            session_service.delete_todos(session_id)
            return {"message": f"Todos deleted from session {session_id}."}, 200
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except Exception as e:
            return {"message": str(e)}, 500
