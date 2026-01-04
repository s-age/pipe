"""Unit tests for ApplyDoctorModificationsAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.session_optimization import DoctorResult, SessionModifications
from pipe.core.services.session_optimization_service import DoctorResultResponse
from pipe.web.actions.therapist.apply_doctor_modifications_action import (
    ApplyDoctorModificationsAction,
)
from pipe.web.requests.therapist_requests import ApplyDoctorRequest


class TestApplyDoctorModificationsAction:
    """Unit tests for ApplyDoctorModificationsAction."""

    @patch("pipe.web.service_container.get_session_workflow_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution of apply doctor modifications."""
        # Setup
        session_id = "test-session-123"
        modifications = SessionModifications(
            deletions=[1, 2],
            edits=[],
            compressions=[],
        )

        mock_request = MagicMock(spec=ApplyDoctorRequest)
        mock_request.session_id = session_id
        mock_request.modifications = modifications

        expected_result = DoctorResultResponse(
            session_id="doctor-session-456",
            result=DoctorResult(
                status="Succeeded",
                reason="Modifications applied successfully",
                applied_deletions=[1, 2],
                applied_edits=[],
                applied_compressions=[],
            ),
        )

        mock_service = MagicMock()
        mock_service.run_takt_for_doctor.return_value = expected_result
        mock_get_service.return_value = mock_service

        action = ApplyDoctorModificationsAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Verify
        assert result == expected_result
        mock_service.run_takt_for_doctor.assert_called_once_with(
            session_id, modifications
        )

    @patch("pipe.web.service_container.get_session_workflow_service")
    def test_execute_service_error(self, mock_get_service: MagicMock) -> None:
        """Test execution when the workflow service raises an error."""
        # Setup
        mock_request = MagicMock(spec=ApplyDoctorRequest)
        mock_request.session_id = "test-session-123"
        mock_request.modifications = SessionModifications(
            deletions=[],
            edits=[],
            compressions=[],
        )

        mock_service = MagicMock()
        mock_service.run_takt_for_doctor.side_effect = Exception(
            "Workflow service error"
        )
        mock_get_service.return_value = mock_service

        action = ApplyDoctorModificationsAction(validated_request=mock_request)

        # Execute & Verify
        with pytest.raises(Exception, match="Workflow service error"):
            action.execute()
        mock_service.run_takt_for_doctor.assert_called_once()
