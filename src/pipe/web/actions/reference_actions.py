from typing import Any

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_reference_persist import (
    EditReferencePersistRequest,
)
from pipe.web.requests.sessions.edit_reference_ttl import EditReferenceTtlRequest
from pipe.web.requests.sessions.edit_references import EditReferencesRequest
from pydantic import ValidationError


class ReferencesEditAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        if not session_id:
            return {"message": "session_id is required"}, 400

        try:
            request_data = EditReferencesRequest(**self.request_data.get_json())
            get_session_service().update_references(session_id, request_data.references)
            return {"message": f"Session {session_id} references updated."}, 200
        except ValidationError as e:
            return {"message": str(e)}, 422
        except FileNotFoundError:
            return {"message": "Session not found."}, 404
        except Exception as e:
            return {"message": str(e)}, 500


class ReferencePersistEditAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        reference_index = self.params.get("reference_index")

        if not session_id or reference_index is None:
            return {"message": "session_id and reference_index are required"}, 400

        try:
            reference_index = int(reference_index)
        except ValueError:
            return {"message": "reference_index must be an integer"}, 400

        try:
            request_data = EditReferencePersistRequest(**self.request_data.get_json())
            new_persist_state = request_data.persist

            session = get_session_service().get_session(session_id)
            if not session:
                return {"message": "Session not found."}, 404

            if not (0 <= reference_index < len(session.references)):
                return {"message": "Reference index out of range."}, 400

            file_path = session.references[reference_index].path
            get_session_service().update_reference_persist_in_session(
                session_id, file_path, new_persist_state
            )

            return {
                "message": f"Persist state for reference {reference_index} updated.",
            }, 200
        except ValidationError as e:
            return {"message": str(e)}, 422
        except Exception as e:
            return {"message": str(e)}, 500


class ReferenceToggleDisabledAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        reference_index = self.params.get("reference_index")

        if not session_id or reference_index is None:
            return {"message": "session_id and reference_index are required"}, 400

        try:
            reference_index = int(reference_index)
        except ValueError:
            return {"message": "reference_index must be an integer"}, 400

        try:
            session = get_session_service().get_session(session_id)
            if not session:
                return {"message": "Session not found."}, 404

            if not (0 <= reference_index < len(session.references)):
                return {"message": "Reference index out of range."}, 400

            file_path = session.references[reference_index].path
            service = get_session_service()
            service.toggle_reference_disabled_in_session(session_id, file_path)

            # Get the new disabled state
            updated_session = get_session_service().get_session(session_id)
            new_disabled_state = updated_session.references[reference_index].disabled

            return {
                "message": f"Disabled state for reference {reference_index} toggled.",
                "disabled": new_disabled_state,
            }, 200
        except Exception as e:
            return {"message": str(e)}, 500


class ReferenceTtlEditAction(BaseAction):
    def execute(self) -> tuple[dict[str, Any], int]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        reference_index = self.params.get("reference_index")

        if not session_id or reference_index is None:
            return {"message": "session_id and reference_index are required"}, 400

        try:
            reference_index = int(reference_index)
        except ValueError:
            return {"message": "reference_index must be an integer"}, 400

        try:
            request_data = EditReferenceTtlRequest(**self.request_data.get_json())
            new_ttl = request_data.ttl

            session = get_session_service().get_session(session_id)
            if not session:
                return {"message": "Session not found."}, 404

            if not (0 <= reference_index < len(session.references)):
                return {"message": "Reference index out of range."}, 400

            file_path = session.references[reference_index].path
            get_session_service().update_reference_ttl_in_session(
                session_id, file_path, new_ttl
            )

            return {
                "message": f"TTL for reference {reference_index} updated.",
            }, 200
        except ValidationError as e:
            return {"message": str(e)}, 422
        except Exception as e:
            return {"message": str(e)}, 500
