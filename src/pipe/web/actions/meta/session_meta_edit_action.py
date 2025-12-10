"""Session meta edit action."""

from pipe.web.actions.base_action import BaseAction
from pipe.web.exceptions import NotFoundError
from pipe.web.requests.sessions.edit_session_meta import EditSessionMetaRequest


class SessionMetaEditAction(BaseAction):
    request_model = EditSessionMetaRequest

    def execute(self) -> dict[str, str]:
        from pipe.web.service_container import get_session_meta_service

        request = self.validated_request

        try:
            get_session_meta_service().edit_session_meta(
                request.session_id,
                request.model_dump(exclude_unset=True, exclude={"session_id"}),
            )
            return {"message": f"Session {request.session_id} metadata updated."}
        except FileNotFoundError:
            raise NotFoundError("Session not found.")
