"""Unit tests for SessionMetaEditAction."""

from unittest.mock import MagicMock, patch

import pytest
from pipe.core.models.session import SessionMetaUpdate
from pipe.web.action_responses import SuccessMessageResponse
from pipe.web.actions.meta.session_meta_edit_action import SessionMetaEditAction
from pipe.web.requests.sessions.edit_session_meta import EditSessionMetaRequest


class TestSessionMetaEditAction:
    """Unit tests for SessionMetaEditAction."""

    @pytest.fixture
    def mock_service(self):
        """Mock SessionMetaService."""
        return MagicMock()

    @patch("pipe.web.service_container.get_session_meta_service")
    def test_execute_success(self, mock_get_service, mock_service):
        """Test successful execution of session meta edit action with partial fields."""
        mock_get_service.return_value = mock_service

        # Setup validated request
        mock_request = MagicMock(spec=EditSessionMetaRequest)
        mock_request.session_id = "test-session"
        # Simulate model_dump behavior
        mock_request.model_dump.return_value = {
            "purpose": "New purpose",
            "background": "New background",
        }

        action = SessionMetaEditAction(validated_request=mock_request)

        response = action.execute()

        # Verify service call
        mock_get_service.assert_called_once()
        # Verify model_dump call
        mock_request.model_dump.assert_called_once_with(
            exclude={"session_id"}, exclude_unset=True
        )

        # Verify edit_session_meta call
        mock_service.edit_session_meta.assert_called_once()
        args, _ = mock_service.edit_session_meta.call_args
        assert args[0] == "test-session"
        update_data = args[1]
        assert isinstance(update_data, SessionMetaUpdate)
        assert update_data.purpose == "New purpose"
        assert update_data.background == "New background"
        assert update_data.roles is None

        # Verify response
        assert isinstance(response, SuccessMessageResponse)
        assert response.message == "Session metadata updated successfully"

    @patch("pipe.web.service_container.get_session_meta_service")
    def test_execute_all_supported_fields(self, mock_get_service, mock_service):
        """Test execution with all fields supported by SessionMetaUpdate."""
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=EditSessionMetaRequest)
        mock_request.session_id = "test-session"
        update_fields = {
            "purpose": "purpose",
            "background": "background",
            "roles": ["role1"],
            "artifacts": ["art1"],
            "procedure": "proc",
            "multi_step_reasoning_enabled": True,
        }
        mock_request.model_dump.return_value = update_fields

        action = SessionMetaEditAction(validated_request=mock_request)
        action.execute()

        args, _ = mock_service.edit_session_meta.call_args
        update_data = args[1]
        assert update_data.purpose == "purpose"
        assert update_data.background == "background"
        assert update_data.roles == ["role1"]
        assert update_data.artifacts == ["art1"]
        assert update_data.procedure == "proc"
        assert update_data.multi_step_reasoning_enabled is True

    @patch("pipe.web.service_container.get_session_meta_service")
    def test_execute_handles_extra_fields(self, mock_get_service, mock_service):
        """Test that extra fields in request are handled (ignored by SessionMetaUpdate)."""
        mock_get_service.return_value = mock_service

        mock_request = MagicMock(spec=EditSessionMetaRequest)
        mock_request.session_id = "test-session"
        # token_count and hyperparameters are in EditSessionMetaRequest but not SessionMetaUpdate
        update_fields = {
            "purpose": "purpose",
            "token_count": 100,
            "hyperparameters": {"temperature": 0.7},
        }
        mock_request.model_dump.return_value = update_fields

        action = SessionMetaEditAction(validated_request=mock_request)

        # This should not raise ValidationError if Pydantic ignores extra fields
        action.execute()

        args, _ = mock_service.edit_session_meta.call_args
        update_data = args[1]
        assert update_data.purpose == "purpose"
        # Verify that extra fields didn't break anything (they are just not in update_data)
        assert not hasattr(update_data, "token_count")
