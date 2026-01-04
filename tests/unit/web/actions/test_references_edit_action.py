"""Unit tests for ReferencesEditAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.reference import Reference
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.reference.references_edit_action import ReferencesEditAction
from pipe.web.requests.sessions.edit_references import EditReferencesRequest


class TestReferencesEditAction:
    """Tests for ReferencesEditAction."""

    @patch("pipe.web.service_container.get_session_reference_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of references edit action."""
        # Setup mocks
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        session_id = "test-session"
        references = [
            Reference(path="file1.py", disabled=False),
            Reference(path="file2.py", disabled=True),
        ]

        # Create validated request
        mock_request = MagicMock(spec=EditReferencesRequest)
        mock_request.session_id = session_id
        mock_request.references = references

        # Initialize action
        action = ReferencesEditAction(validated_request=mock_request)

        # Execute
        response = action.execute()

        # Verify
        assert isinstance(response, SuccessMessageResponse)
        assert response.message == "References updated successfully"

        mock_service.update_references.assert_called_once_with(session_id, references)

    @patch("pipe.web.service_container.get_session_reference_service")
    def test_execute_service_raises_error(self, mock_get_service: MagicMock) -> None:
        """Test execution when service raises an error."""
        # Setup mocks
        mock_service = MagicMock()
        mock_service.update_references.side_effect = ValueError("Invalid session")
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=EditReferencesRequest)
        mock_request.session_id = "invalid-session"
        mock_request.references = []

        action = ReferencesEditAction(validated_request=mock_request)

        # Execute and verify exception propagates
        with pytest.raises(ValueError, match="Invalid session"):
            action.execute()
