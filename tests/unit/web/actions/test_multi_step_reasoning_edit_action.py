"""Unit tests for MultiStepReasoningEditAction."""

from unittest.mock import MagicMock, patch

from pipe.web.actions.meta.multi_step_reasoning_edit_action import (
    MultiStepReasoningEditAction,
)
from pipe.web.requests.sessions.edit_multi_step_reasoning import (
    EditMultiStepReasoningRequest,
)


class TestMultiStepReasoningEditAction:
    """Tests for MultiStepReasoningEditAction."""

    @patch("pipe.web.service_container.get_session_meta_service")
    @patch("pipe.web.service_container.get_session_service")
    def test_execute_success(
        self, mock_get_session_service, mock_get_session_meta_service
    ):
        """Test successful execution of MultiStepReasoningEditAction."""
        # Arrange
        session_id = "test-session-123"
        enabled = True

        # Mock request
        mock_request = MagicMock(spec=EditMultiStepReasoningRequest)
        mock_request.session_id = session_id
        mock_request.multi_step_reasoning_enabled = enabled

        # Mock services
        mock_meta_service = MagicMock()
        mock_get_session_meta_service.return_value = mock_meta_service

        mock_session_service = MagicMock()
        mock_get_session_service.return_value = mock_session_service

        # Mock session object
        mock_session = MagicMock()
        mock_session_data = {
            "sessionId": session_id,
            "multiStepReasoningEnabled": enabled,
        }
        mock_session.model_dump.return_value = mock_session_data
        mock_session_service.get_session.return_value = mock_session

        # Instantiate action
        action = MultiStepReasoningEditAction(validated_request=mock_request)

        # Act
        result = action.execute()

        # Assert
        # Verify meta service call
        mock_get_session_meta_service.assert_called_once()
        args, _ = mock_meta_service.edit_session_meta.call_args
        assert args[0] == session_id
        update_data = args[1]
        assert update_data.multi_step_reasoning_enabled == enabled

        # Verify session service call
        mock_get_session_service.assert_called_once()
        mock_session_service.get_session.assert_called_once_with(session_id)

        # Verify result
        assert (
            result["message"] == f"Session {session_id} multi-step reasoning updated."
        )
        assert result["session"] == mock_session_data
        mock_session.model_dump.assert_called_once_with(
            by_alias=True, exclude_none=False
        )

    @patch("pipe.web.service_container.get_session_meta_service")
    @patch("pipe.web.service_container.get_session_service")
    def test_execute_disable_reasoning(
        self, mock_get_session_service, mock_get_session_meta_service
    ):
        """Test successful execution when disabling multi-step reasoning."""
        # Arrange
        session_id = "test-session-456"
        enabled = False

        # Mock request
        mock_request = MagicMock(spec=EditMultiStepReasoningRequest)
        mock_request.session_id = session_id
        mock_request.multi_step_reasoning_enabled = enabled

        # Mock services
        mock_meta_service = MagicMock()
        mock_get_session_meta_service.return_value = mock_meta_service

        mock_session_service = MagicMock()
        mock_get_session_service.return_value = mock_session_service

        # Mock session object
        mock_session = MagicMock()
        mock_session_data = {
            "sessionId": session_id,
            "multiStepReasoningEnabled": enabled,
        }
        mock_session.model_dump.return_value = mock_session_data
        mock_session_service.get_session.return_value = mock_session

        # Instantiate action
        action = MultiStepReasoningEditAction(validated_request=mock_request)

        # Act
        result = action.execute()

        # Assert
        args, _ = mock_meta_service.edit_session_meta.call_args
        assert args[1].multi_step_reasoning_enabled == enabled
        assert result["session"]["multiStepReasoningEnabled"] is False
