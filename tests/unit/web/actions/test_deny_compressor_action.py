"""Unit tests for DenyCompressorAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.web.actions.compress.deny_compressor_action import DenyCompressorAction
from pipe.web.requests.compress_requests import DenyCompressorRequest


class TestDenyCompressorAction:
    """Tests for DenyCompressorAction."""

    @patch("pipe.web.service_container.get_session_optimization_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of deny compression."""
        # Setup
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=DenyCompressorRequest)
        mock_request.session_id = "test-session-123"

        action = DenyCompressorAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Verify
        assert result is None
        mock_service.deny_compression.assert_called_once_with("test-session-123")

    @patch("pipe.web.service_container.get_session_optimization_service")
    def test_execute_service_error(self, mock_get_service: MagicMock) -> None:
        """Test execution when service raises an error."""
        # Setup
        mock_service = MagicMock()
        mock_service.deny_compression.side_effect = Exception("Service error")
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=DenyCompressorRequest)
        mock_request.session_id = "test-session-123"

        action = DenyCompressorAction(validated_request=mock_request)

        # Execute & Verify
        with pytest.raises(Exception, match="Service error"):
            action.execute()

        mock_service.deny_compression.assert_called_once_with("test-session-123")
