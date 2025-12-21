"""Artifacts edit action."""

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_artifacts import EditArtifactsRequest


class ArtifactsEditAction(BaseAction):
    request_model = EditArtifactsRequest

    def execute(self) -> SuccessMessageResponse:
        from pipe.web.service_container import get_session_artifact_service

        request = self.validated_request

        get_session_artifact_service().update_artifacts(
            request.session_id, request.artifacts
        )

        return SuccessMessageResponse(message="Artifacts updated successfully")
