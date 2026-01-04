"""Unit tests for CreateCompressorSessionAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.services.session_optimization_service import CompressorResult
from pipe.web.actions.compress.create_compressor_session_action import (
    CreateCompressorSessionAction,
)
from pipe.web.requests.compress_requests import CreateCompressorRequest


class TestCreateCompressorSessionAction:
    """Tests for CreateCompressorSessionAction."""

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock CreateCompressorRequest."""
        mock = MagicMock(spec=CreateCompressorRequest)
        mock.session_id = "test-session"
        mock.policy = "standard"
        mock.target_length = 100
        mock.start_turn = 1
        mock.end_turn = 5
        return mock

    @pytest.fixture
    def action(self, mock_request: MagicMock) -> CreateCompressorSessionAction:
        """Create a CreateCompressorSessionAction instance."""
        return CreateCompressorSessionAction(validated_request=mock_request)

    @patch("pipe.web.service_container.get_session_optimization_service")
    def test_execute_success(
        self,
        mock_get_service: MagicMock,
        action: CreateCompressorSessionAction,
        mock_request: MagicMock,
    ) -> None:
        """Test successful execution of the action."""
        # Setup mock service
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        expected_result = CompressorResult(
            session_id="compressor-session",
            summary="Test summary",
            verifier_session_id="verifier-session",
        )
        mock_service.run_compression.return_value = expected_result

        # Execute
        result = action.execute()

        # Verify
        assert result == expected_result
        mock_service.run_compression.assert_called_once_with(
            mock_request.session_id,
            mock_request.policy,
            mock_request.target_length,
            mock_request.start_turn,
            mock_request.end_turn,
        )

    @patch("pipe.web.service_container.get_session_optimization_service")
    def test_execute_service_error(
        self, mock_get_service: MagicMock, action: CreateCompressorSessionAction
    ) -> None:
        """Test execution when the service raises an error."""
        # Setup mock service to raise an error
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.run_compression.side_effect = Exception("Service error")

        # Execute and verify
        with pytest.raises(Exception, match="Service error"):
            action.execute()
