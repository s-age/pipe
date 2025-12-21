"""Artifacts edit action."""

from pipe.core.services.session_artifact_service import SessionArtifactService
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.base_action import BaseAction
from pipe.web.requests.sessions.edit_artifacts import EditArtifactsRequest


class ArtifactsEditAction(BaseAction):
    """Edit session artifacts.

    This action uses constructor injection for SessionArtifactService,
    following the DI pattern.
    """

    request_model = EditArtifactsRequest

    def __init__(
        self,
        session_artifact_service: SessionArtifactService,
        validated_request: EditArtifactsRequest | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.session_artifact_service = session_artifact_service
        self.validated_request = validated_request

    def execute(self) -> SuccessMessageResponse:
        if not self.validated_request:
            raise ValueError("Request is required")

        request = self.validated_request

        self.session_artifact_service.update_artifacts(
            request.session_id, request.artifacts
        )

        return SuccessMessageResponse(message="Artifacts updated successfully")
