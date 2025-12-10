"""Reference TTL edit action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_reference_ttl import EditReferenceTtlRequest


class ReferenceTtlEditAction(BaseAction):
    request_model = EditReferenceTtlRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_reference_service

        request = self.validated_request
        get_session_reference_service().update_reference_ttl_by_index(
            request.session_id, request.reference_index, request.ttl
        )

        return {"message": f"TTL for reference {request.reference_index} updated."}
