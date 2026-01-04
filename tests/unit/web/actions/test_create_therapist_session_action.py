"""Unit tests for CreateTherapistSessionAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.services.session_optimization_service import TherapistResult
from pipe.web.actions.therapist.create_therapist_session_action import (
    CreateTherapistSessionAction,
)
from pipe.web.requests.therapist_requests import CreateTherapistRequest


class TestCreateTherapistSessionAction:
    """Tests for CreateTherapistSessionAction."""

    @patch("pipe.web.service_container.get_session_optimization_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of the action."""
        # Setup
        session_id = "test-session-123"
        mock_request = MagicMock(spec=CreateTherapistRequest)
        mock_request.session_id = session_id

        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_result = MagicMock(spec=TherapistResult)
        mock_service.run_therapist.return_value = mock_result

        action = CreateTherapistSessionAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Verify
        assert result == mock_result
        mock_get_service.assert_called_once()
        mock_service.run_therapist.assert_called_once_with(session_id)

    @patch("pipe.web.service_container.get_session_optimization_service")
    def test_execute_service_error(self, mock_get_service: MagicMock) -> None:
        """Test execution when the service raises an error."""
        # Setup
        session_id = "test-session-123"
        mock_request = MagicMock(spec=CreateTherapistRequest)
        mock_request.session_id = session_id

        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.run_therapist.side_effect = Exception("Service error")

        action = CreateTherapistSessionAction(validated_request=mock_request)

        # Execute & Verify
        with pytest.raises(Exception, match="Service error"):
            action.execute()

        mock_get_service.assert_called_once()
        mock_service.run_therapist.assert_called_once_with(session_id)
