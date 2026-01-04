"""Unit tests for HyperparametersEditAction."""

from unittest.mock import MagicMock, patch

from pipe.core.models.hyperparameters import Hyperparameters
from pipe.web.actions.meta.hyperparameters_edit_action import HyperparametersEditAction
from pipe.web.requests.sessions.edit_hyperparameters import EditHyperparametersRequest


class TestHyperparametersEditAction:
    """Tests for the HyperparametersEditAction class."""

    @patch("pipe.web.service_container.get_session_meta_service")
    def test_execute_success(self, mock_get_service: MagicMock) -> None:
        """Test successful execution with all hyperparameters provided."""
        # Setup mock service and session
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_session = MagicMock()
        expected_session_dict = {
            "sessionId": "test-session-123",
            "hyperparameters": {"temperature": 0.5, "topP": 0.9, "topK": 40},
        }
        mock_session.model_dump.return_value = expected_session_dict
        mock_service.update_hyperparameters.return_value = mock_session

        # Mock validated request
        mock_request = MagicMock(spec=EditHyperparametersRequest)
        mock_request.session_id = "test-session-123"
        mock_request.temperature = 0.5
        mock_request.top_p = 0.9
        mock_request.top_k = 40

        action = HyperparametersEditAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Assertions
        assert result["message"] == "Session test-session-123 hyperparameters updated."
        assert result["session"] == expected_session_dict

        # Verify service call
        mock_service.update_hyperparameters.assert_called_once()
        args, _ = mock_service.update_hyperparameters.call_args
        assert args[0] == "test-session-123"
        assert isinstance(args[1], Hyperparameters)
        assert args[1].temperature == 0.5
        assert args[1].top_p == 0.9
        assert args[1].top_k == 40

        # Verify model_dump call
        mock_session.model_dump.assert_called_once_with(
            by_alias=True, exclude_none=False
        )

    @patch("pipe.web.service_container.get_session_meta_service")
    def test_execute_partial_fields(self, mock_get_service: MagicMock) -> None:
        """Test execution with only partial hyperparameters provided."""
        # Setup mock service and session
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_session = MagicMock()
        expected_session_dict = {
            "sessionId": "test-session-123",
            "hyperparameters": {"temperature": 0.7, "topP": None, "topK": None},
        }
        mock_session.model_dump.return_value = expected_session_dict
        mock_service.update_hyperparameters.return_value = mock_session

        # Mock validated request with partial fields
        mock_request = MagicMock(spec=EditHyperparametersRequest)
        mock_request.session_id = "test-session-123"
        mock_request.temperature = 0.7
        mock_request.top_p = None
        mock_request.top_k = None

        action = HyperparametersEditAction(validated_request=mock_request)

        # Execute
        result = action.execute()

        # Assertions
        assert result["message"] == "Session test-session-123 hyperparameters updated."
        assert result["session"] == expected_session_dict

        # Verify service call
        mock_service.update_hyperparameters.assert_called_once()
        # Note: update_hyperparameters is called with (session_id, hyperparameters)
        args, _ = mock_service.update_hyperparameters.call_args
        hp = args[1]
        assert hp.temperature == 0.7
        assert hp.top_p is None
        assert hp.top_k is None
