"""Unit tests for ApproveCompressorAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.compress.approve_compressor_action import ApproveCompressorAction
from pipe.web.requests.compress_requests import ApproveCompressorRequest


class TestApproveCompressorAction:
    """Tests for ApproveCompressorAction."""

    @patch("pipe.web.service_container.get_session_optimization_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of approve compressor action."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        session_id = "test-session-123"
        mock_request = MagicMock(spec=ApproveCompressorRequest)
        mock_request.session_id = session_id

        action = ApproveCompressorAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Verify
        mock_service.approve_compression.assert_called_once_with(session_id)
        assert isinstance(result, SuccessMessageResponse)
        assert result.message == "Compression approved"

    @patch("pipe.web.service_container.get_session_optimization_service")
    def test_execute_service_error(self, mock_get_service: MagicMock) -> None:
        """Test execution when optimization service raises an error."""
        # Setup
        mock_service = MagicMock()
        mock_service.approve_compression.side_effect = Exception("Service error")
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=ApproveCompressorRequest)
        mock_request.session_id = "test-session-123"

        action = ApproveCompressorAction(validated_request=mock_request)

        # Execute & Verify
        with pytest.raises(Exception, match="Service error"):
            action.execute()
