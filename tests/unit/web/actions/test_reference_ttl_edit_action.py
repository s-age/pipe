"""Unit tests for ReferenceTtlEditAction."""

from unittest.mock import MagicMock, patch

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.reference.reference_ttl_edit_action import ReferenceTtlEditAction
from pipe.web.requests.sessions.edit_reference_ttl import EditReferenceTtlRequest


class TestReferenceTtlEditAction:
    """Tests for ReferenceTtlEditAction."""

    @patch("pipe.web.service_container.get_session_reference_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of ReferenceTtlEditAction."""
        # Setup mocks
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Create a mock validated request
        mock_request = MagicMock(spec=EditReferenceTtlRequest)
        mock_request.session_id = "test-session"
        mock_request.reference_index = 1
        mock_request.ttl = 10

        # Initialize action with the mock request
        action = ReferenceTtlEditAction(validated_request=mock_request)

        # Execute
        response = action.execute()

        # Verify service call
        mock_service.update_reference_ttl_by_index.assert_called_once_with(
            "test-session", 1, 10
        )

        # Verify response
        assert isinstance(response, SuccessMessageResponse)
        assert response.message == "Reference TTL updated successfully"
