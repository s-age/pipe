"""Unit tests for ReferencePersistEditAction."""

from unittest.mock import MagicMock, patch

from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.reference.reference_persist_edit_action import (
    ReferencePersistEditAction,
)
from pipe.web.requests.sessions.edit_reference_persist import (
    EditReferencePersistRequest,
)


class TestReferencePersistEditAction:
    """Tests for ReferencePersistEditAction."""

    @patch("pipe.web.service_container.get_session_reference_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of ReferencePersistEditAction."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=EditReferencePersistRequest)
        mock_request.session_id = "test-session"
        mock_request.reference_index = 0
        mock_request.persist = True

        action = ReferencePersistEditAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Verify
        mock_service.update_reference_persist_by_index.assert_called_once_with(
            "test-session", 0, True
        )
        assert isinstance(result, SuccessMessageResponse)
        assert result.message == "Reference persist updated successfully"

    @patch("pipe.web.service_container.get_session_reference_service")
    def test_execute_persist_false(self, mock_get_service: MagicMock) -> None:
        """Test execution with persist=False."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=EditReferencePersistRequest)
        mock_request.session_id = "test-session"
        mock_request.reference_index = 1
        mock_request.persist = False

        action = ReferencePersistEditAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Verify
        mock_service.update_reference_persist_by_index.assert_called_once_with(
            "test-session", 1, False
        )
        assert isinstance(result, SuccessMessageResponse)
        assert result.message == "Reference persist updated successfully"
