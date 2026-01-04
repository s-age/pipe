"""Unit tests for ArtifactsEditAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.services.session_artifact_service import SessionArtifactService
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.artifact.artifacts_edit_action import ArtifactsEditAction
from pipe.web.requests.sessions.edit_artifacts import EditArtifactsRequest


class TestArtifactsEditAction:
    """Tests for ArtifactsEditAction."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock SessionArtifactService."""
        return MagicMock(spec=SessionArtifactService)

    @pytest.fixture
    def mock_request(self):
        """Create a mock EditArtifactsRequest."""
        request = MagicMock(spec=EditArtifactsRequest)
        request.session_id = "test-session-123"
        request.artifacts = [MagicMock(), MagicMock()]
        return request

    def test_init(self, mock_service, mock_request):
        """Test initialization of ArtifactsEditAction."""
        action = ArtifactsEditAction(
            session_artifact_service=mock_service, validated_request=mock_request
        )
        assert action.session_artifact_service == mock_service
        assert action.validated_request == mock_request

    @patch("pipe.web.actions.artifact.artifacts_edit_action.SuccessMessageResponse")
    def test_execute_success(self, mock_response_class, mock_service, mock_request):
        """Test successful execution of ArtifactsEditAction."""
        action = ArtifactsEditAction(
            session_artifact_service=mock_service, validated_request=mock_request
        )

        # Setup mock response
        mock_response_instance = MagicMock(spec=SuccessMessageResponse)
        mock_response_class.return_value = mock_response_instance

        response = action.execute()

        # Verify service call
        mock_service.update_artifacts.assert_called_once_with(
            "test-session-123", mock_request.artifacts
        )

        # Verify response creation
        mock_response_class.assert_called_once_with(
            message="Artifacts updated successfully"
        )
        assert response == mock_response_instance

    def test_execute_missing_request(self, mock_service):
        """Test execution when validated_request is missing."""
        action = ArtifactsEditAction(session_artifact_service=mock_service)

        with pytest.raises(ValueError, match="Request is required"):
            action.execute()

        # Verify service was not called
        mock_service.update_artifacts.assert_not_called()
