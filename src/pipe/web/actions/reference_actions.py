from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import BadRequestError, NotFoundError
from pipe.web.requests.sessions.edit_reference_persist import (
    EditReferencePersistRequest,
)
from pipe.web.requests.sessions.edit_reference_ttl import EditReferenceTtlRequest
from pipe.web.requests.sessions.edit_references import EditReferencesRequest


class ReferencesEditAction(BaseAction):
    request_model = EditReferencesRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        request = self.validated_request

        try:
            get_session_service().update_references(
                request.session_id, request.references
            )
            return {"message": f"Session {request.session_id} references updated."}
        except FileNotFoundError:
            raise NotFoundError("Session not found.")


class ReferencePersistEditAction(BaseAction):
    request_model = EditReferencePersistRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        reference_index = int(request.reference_index)

        session = get_session_service().get_session(request.session_id)
        if not session:
            raise NotFoundError("Session not found.")

        if not (0 <= reference_index < len(session.references)):
            raise BadRequestError("Reference index out of range.")

        file_path = session.references[reference_index].path
        get_session_service().update_reference_persist_in_session(
            request.session_id, file_path, request.persist
        )

        return {"message": f"Persist state for reference {reference_index} updated."}


class ReferenceToggleDisabledAction(BaseAction):
    # This action doesn't have body validation, only path params
    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        session_id = self.params.get("session_id")
        reference_index = self.params.get("reference_index")

        if not session_id or reference_index is None:
            raise BadRequestError("session_id and reference_index are required")

        try:
            reference_index = int(reference_index)
        except ValueError:
            raise BadRequestError("reference_index must be an integer")

        session = get_session_service().get_session(session_id)
        if not session:
            raise NotFoundError("Session not found.")

        if not (0 <= reference_index < len(session.references)):
            raise BadRequestError("Reference index out of range.")

        file_path = session.references[reference_index].path
        service = get_session_service()
        service.toggle_reference_disabled_in_session(session_id, file_path)

        # Get the new disabled state
        updated_session = get_session_service().get_session(session_id)
        new_disabled_state = updated_session.references[reference_index].disabled

        return {
            "message": f"Disabled state for reference {reference_index} toggled.",
            "disabled": str(new_disabled_state),
        }


class ReferenceTtlEditAction(BaseAction):
    request_model = EditReferenceTtlRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_service

        request = self.validated_request
        reference_index = int(request.reference_index)

        session = get_session_service().get_session(request.session_id)
        if not session:
            raise NotFoundError("Session not found.")

        if not (0 <= reference_index < len(session.references)):
            raise BadRequestError("Reference index out of range.")

        file_path = session.references[reference_index].path
        get_session_service().update_reference_ttl_in_session(
            request.session_id, file_path, request.ttl
        )

        return {"message": f"TTL for reference {reference_index} updated."}
